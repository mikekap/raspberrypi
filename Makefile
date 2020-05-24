.PHONY: base unifi

base:
	cd base && docker build -t rpi-base .

unifi: base
	cd unifi && docker build -t rpi-unifi .
