all:
	rm -rf output
	npm install
	mkdir -p output/beta/js
	mkdir -p output/beta/css
	cp node_modules/mdbootstrap/js/bootstrap.min.js output/beta/js/
	cp node_modules/mdbootstrap/css/bootstrap.min.css output/beta/css/
	cp node_modules/mdbootstrap/css/mdb.min.css output/beta/css/
	cp node_modules/jquery/dist/jquery.min.js output/beta/js/
	python src/gen_webpage.py
	python src/gen_volume.py 12
	python src/gen_volume.py 13
	python src/gen_volume.py 14
	python src/gen_volume.py 15
	python src/gen_volume.py 16
	python src/gen_volume.py 17
	python src/gen_volume.py 18
	python src/gen_volume.py 19
	python src/gen_volume.py 20
	python src/gen_volume.py 21
	cp -r static/img/ output/
	cp -r static/img/ output/beta/
	cp -r static/css/ output/beta/
	cp -r static/img/ output/beta/

test:
	py.test -vv src/tests/test.py

develop:
	livereload -p 8001 output/

update:
	git submodule foreach git pull origin master
	git pull origin master
	git submodule foreach git pull origin master
