PWD := $(shell pwd)
KERNEL_DIR ?=/lib/modules/$(shell uname -r)/build

DRV_NAME := my_module
obj-m := $(DRV_NAME).o

.PHONY: build run remove install uninstall clean check

build:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

run:
	insmod $(PWD)/$(DRV_NAME).ko

remove:
	rmmod $(DRV_NAME).ko

install:
	cp $(DRV_NAME).ko /lib/modules/$(shell uname -r)
	/sbin/depmod -a
	/sbin/modprobe $(DRV_NAME)

uninstall:
	/sbin/modprobe -r $(DRV_NAME)
	rm -f /lib/modules/$(shell uname -r)/$(DRV_NAME).ko
	/sbin/depmod -a

clean:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean

check:
	@echo "=== Запуск проверки модуля ==="
	$(MAKE) remove
	$(MAKE) build
	$(MAKE) run
	python3 ./check/check.py
	$(MAKE) remove
	$(MAKE) clean