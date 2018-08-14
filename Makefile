all:
	rm -rf output
	npm install
	mkdir -p output
	mkdir -p output/js
	mkdir -p output/css
	cp node_modules/bootstrap/dist/js/bootstrap.min.js output/js/
	cp node_modules/bootstrap/dist/css/bootstrap.min.css output/css/
	cp node_modules/jquery/dist/jquery.min.js output/js/
	python bin/generate.py
	cp -r img/ output/
	cp -r css/ output/

test:
	! html_lint.py --disable=names output/*.html | grep Error

develop:
	python -m http.server 8001 --directory output

upload:
	python bin/upload.py
