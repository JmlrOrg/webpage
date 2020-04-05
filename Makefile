VOLUMES = 11 12 13 14 15 16 17 18 19 20 21
VOLUMES = 11

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
	$(foreach vol,$(VOLUMES),python src/gen_volume.py $(vol);)
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
