microstackcommon
============

Common functions for interacting with Microstack products.

Contains some core helper functions and pure Python drivers for accessing
GPIO pins, SPI and I2C busses.

Currently in active development. Still need to experiment with SMBus for
Python 3.


Documentation
=============

[http://microstack.github.io/microstackcommon/](http://microstack.github.io/microstackcommon/)

You can also find the documentation installed at:

    /usr/share/doc/python3-microstackcommon/

Install
=======

Make sure you are using the lastest version of Raspbian:

    $ sudo apt-get update
    $ sudo apt-get upgrade

Install `microstackcommon` (for Python 3 and 2) with the following command:

    $ sudo apt-get install python{,3}-microstackcommon

You will also need to set up automatic loading of the SPI kernel module which
can be done with the lastest version of `raspi-config`. Run:

    $ sudo raspi-config

Then navigate to `Advanced Options`, `SPI` and select `yes`.
