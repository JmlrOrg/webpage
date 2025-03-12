SHELL := /bin/bash

all: static

clean:
	rm -rf output

npm: clean
	npm install
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
	python src/gen_webpage.py

static: webpage
	cp -r static/img/ output/
	cp -r static/img/ output/beta/
	cp -r static/css/ output/beta/
	cp -r static/img/ output/beta/

test:
	py.test -vv src/tests/test.py

develop:
	livereload -p 8001 output/

update:
	git submodule foreach git pull origin main
	git pull origin main
	git submodule foreach git submodule update

upload:
	aws s3 sync --region us-east-1 --acl public-read --exclude "js/*" output/ s3://jmlr.org

upload_html:
	aws s3 sync --region us-east-1 --acl public-read --exclude "js/*" --exclude "*.pdf" output/ s3://jmlr.org

circle_upload:
	aws s3 sync --region us-east-1 --acl public-read --exclude "js/*" output/output/ s3://jmlr.org
