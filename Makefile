SHELL = /bin/bash


.ONESHELL:

env:
	python3 -m venv venv
	source venv/bin/activate
	pip3 install -r requirements.txt

exe:
	source venv/bin/activate
	pyinstaller --onefile src/main.py
	cp -r src/figure src/config.ini dist
	cd dist && ./main

run:
	source venv/bin/activate
	cd src && python3 main.py