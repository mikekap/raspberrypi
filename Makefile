.PHONY: base unifi light-control
all: base unifi light-control

base:
	cd base && docker build -t rpi-base .

unifi: base
	cd unifi && docker build -t rpi-unifi .

light-control:
	cd light-control && docker build -t rpi-light-control .
