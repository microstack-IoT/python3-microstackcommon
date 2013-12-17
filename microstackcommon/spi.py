import sys
import posix
import struct
import ctypes
from .linux_spi_spidev import *
from fcntl import ioctl


SPIDEV = '/dev/spidev'
SPI_HELP = "`sudo raspi-config`, Advanced, Enable SPI, yes."


def _py2bytes(bytes_to_send):
    """Converts a list of bytes to Python 2 bytes."""
    return "".join([chr(b) for b in bytes_to_send])


def _py3bytes(bytes_to_send):
    """Converts a list of bytes to Python 3 bytes."""
    return bytes((bytes_to_send))


def _py2ord(bytes_to_ord):
    """Converts a list of bytes to Python 2 bytes."""
    return [ord(b) for b in bytes_to_ord]


def _py3ord(bytes_to_ord):
    """Converts a list of bytes to Python 3 bytes."""
    return bytes_to_ord


PY3 = sys.version_info[0] >= 3
_pybytes = _py3bytes if PY3 else _py2bytes
_pyord = _py3ord if PY3 else _py2ord


class SPIInitError(Exception):
    pass


class SPIDevice(object):
    """An SPI Device at /dev/spi<bus>.<chip_select>."""
    def __init__(self, bus=0, chip_select=0, spi_transaction_callback=None):
        """Initialises the SPI device file descriptor.

        :param bus: The SPI device bus number
        :type bus: int
        :param chip_select: The SPI device chip_select number
        :param chip_select: int
        :raises: InitError
        """
        self.bus = bus
        self.chip_select = chip_select
        self.spi_transaction_callback = spi_transaction_callback
        self.fd = None
        spi_device_string = "%s%d.%d" % (SPIDEV, self.bus, self.chip_select)
        self.open_fd(spi_device_string)

    def __del__(self):
        if self.fd is not None:
            self.close_fd()

    def open_fd(self, spi_device_string):
        """Opens the SPI device file descriptor."""
        try:
            self.fd = posix.open(spi_device_string, posix.O_RDWR)
        except OSError as e:
            raise SPIInitError(
                "I can't see %s. Have you enabled the SPI module? (%s)"
                % (spi_device_string, SPI_HELP)
            )  # from e  # from is only available in Python 3

    def close_fd(self):
        """Closes the SPI device file descriptor."""
        posix.close(self.fd)
        self.fd = None

    def transaction(self, bytes_to_send):
        """Sends bytes via the SPI bus.

        :param bytes_to_send: The bytes to send on the SPI device.
        :type bytes_to_send: bytes
        :returns: bytes -- returned bytes from SPI device
        :raises: InitError
        """
        bytes_to_send = _pybytes(bytes_to_send)

        # make some buffer space to store reading/writing
        wbuffer = ctypes.create_string_buffer(bytes_to_send,
                                              len(bytes_to_send))
        rbuffer = ctypes.create_string_buffer(len(bytes_to_send))

        # create the spi transfer struct
        transfer = spi_ioc_transfer(
            tx_buf=ctypes.addressof(wbuffer),
            rx_buf=ctypes.addressof(rbuffer),
            len=ctypes.sizeof(wbuffer))

        if self.spi_transaction_callback is not None:
            self.spi_transaction_callback(bytes_to_send)

        # send the spi command
        ioctl(self.fd, SPI_IOC_MESSAGE(1), transfer)
        return _pyord(ctypes.string_at(rbuffer, ctypes.sizeof(rbuffer)))

    @property
    def clock_mode(self):
        """Returns the current clock mode for the SPI bus."""
        return struct.unpack('c', ioctl(self.fd, SPI_IOC_RD_MODE, " "))[0]

    @clock_mode.setter
    def clock_mode(self, mode):
        """Changes the clock mode for this SPI bus.

        For example:
             #start clock low, sample trailing edge
             spi.clock_mode = SPI_MODE_1
        """
        ioctl(self.fd, SPI_IOC_WR_MODE, struct.pack('I', mode))

    @property
    def speed_hz(self):
        """
        Returns the current speed in Hz for this SPI bus
        """
        return struct.unpack(
            'I', ioctl(self.fd, SPI_IOC_RD_MAX_SPEED_HZ, "    "))[0]

    @speed_hz.setter
    def speed_hz(self, speedhz):
        """
        Changes the speed in Hz for this SPI bus
        """
        ioctl(self.fd, SPI_IOC_WR_MAX_SPEED_HZ, struct.pack('I', speedhz))
