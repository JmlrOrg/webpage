SHELL := /bin/bash
AWS_REGION ?= us-east-1
S3_BUCKET ?= jmlr.org

all: static

clean:
	rm -rf output

npm: clean
	@if [ -f package-lock.json ]; then \
		npm ci --prefer-offline --no-audit; \
	else \
		echo "package-lock.json not found; using npm install"; \
		npm install --prefer-offline --no-audit; \
	fi
	mkdir -p output/beta/js
	mkdir -p output/beta/css
	mkdir -p output/beta/format
	mkdir -p output/format
	mkdir -p output/beta/format
	mkdir -p output/special_issues
	mkdir -p output/beta/special_issues
	cp node_modules/mdbootstrap/js/*.* output/beta/js/
	cp node_modules/mdbootstrap/css/*.* output/beta/css/
	curl 'https://jmlr.csail.mit.edu/manudb/editorial_board?list=action' -o templates/aes.html
	cp templates/aes.html templates/beta/aes.html
	curl 'https://jmlr.csail.mit.edu/manudb/editorial_board' -o templates/reviewers.html
	cp templates/reviewers.html templates/beta/reviewers.html

webpage: npm
	uv run src/gen_webpage.py

static: webpage
	cp -r static/img/ output/
	cp -r static/img/ output/beta/
	cp static/css/style.css output/style.css
	cp static/css/style.css output/beta/css/style.css

test:
	uv run py.test -q src/tests/test.py

develop:
	livereload -p 8001 output/

update:
	git submodule foreach git pull origin main
	git pull origin main
	git submodule foreach git submodule update

upload:
	aws s3 sync --region $(AWS_REGION) --acl public-read --exclude "js/*" output/ s3://$(S3_BUCKET)
	# Keep HTML/XML effectively uncached so page updates appear quickly.
	aws s3 cp --region $(AWS_REGION) --acl public-read --recursive output/ s3://$(S3_BUCKET) --exclude "*" --include "*.html" --include "*.xml" --cache-control "max-age=0, s-maxage=0, must-revalidate" --metadata-directive REPLACE
	@if [ -n "$$CLOUDFRONT_DISTRIBUTION_ID" ]; then \
		echo "Invalidating CloudFront distribution $$CLOUDFRONT_DISTRIBUTION_ID"; \
		aws cloudfront create-invalidation --distribution-id "$$CLOUDFRONT_DISTRIBUTION_ID" --paths "/index.html" "/jmlr.xml" "/papers/*" "/style.css" "/beta/*"; \
	else \
		echo "CLOUDFRONT_DISTRIBUTION_ID not set; skipping CloudFront invalidation"; \
	fi

upload_html:
	aws s3 sync --region $(AWS_REGION) --acl public-read --exclude "js/*" --exclude "*.pdf" output/ s3://$(S3_BUCKET)
	aws s3 cp --region $(AWS_REGION) --acl public-read --recursive output/ s3://$(S3_BUCKET) --exclude "*" --include "*.html" --include "*.xml" --cache-control "max-age=0, s-maxage=0, must-revalidate" --metadata-directive REPLACE

circle_upload:
	aws s3 sync --region $(AWS_REGION) --acl public-read --exclude "js/*" output/output/ s3://$(S3_BUCKET)
