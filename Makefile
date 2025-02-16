.PHONY: base unifi light-control nginx
all: base unifi light-control nginx

base:
	cd base && docker build -t rpi-base .

unifi: base
	cd unifi && docker build -t rpi-unifi .

light-control: base
	cd light-control && docker build -t rpi-light-control .

nginx: base
	cd nginx && docker build -t rpi-nginx .
