microstackcommon
================
Common functions for interacting with Microstack products.

Contains some core helper functions and pure Python drivers for accessing
GPIO pins, SPI and I2C buses.

Currently in active development. Still need to experiment with SMBus for
Python 3.


Install
=======

Make sure you are using the latest version of Raspbian:

    $ sudo apt-get update
    $ sudo apt-get upgrade

Install `microstackcommon` for Python 3 with the following command:

    $ sudo apt-get install python3-microstackcommon

You will also need to set up automatic loading of the SPI kernel module which
can be done with the latest version of `raspi-config`. Run:

    $ sudo raspi-config

Then navigate to `Advanced Options`, `SPI` and select `yes`.
