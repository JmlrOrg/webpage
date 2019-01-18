all:
	rm -rf output
	npm install
	mkdir -p output/beta/js
	mkdir -p output/beta/css
	cp node_modules/bootstrap/dist/js/bootstrap.min.js output/beta/js/
	cp node_modules/bootstrap/dist/css/bootstrap.min.css output/beta/css/
	cp node_modules/jquery/dist/jquery.min.js output/beta/js/
	python src/gen_webpage.py
	python src/gen_volume.py 19
	cp -r static/img/ output/
	cp -r static/css/ output/beta/

test:
	! html_lint.py --disable=entities output/beta/*.html | grep Error
	py.test -vv src/tests/test.py

develop:
	cd output && python -m http.server 8001
