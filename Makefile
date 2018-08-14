all:
	rm -rf ouput/*
	npm install bootstrap
	npm install jquery
	cp -r node_modules/bootstrap output/
	cp -r node_modules/jquery output/
	python bin/generate.py
	cp -r img/ output/
	cp -r css/ output/

test:
	html_lint.py output/*.html

develop:
	python -m http.server 8001 --directory output

upload:
	python bin/upload.py
