import subprocess
import time
import microstackcommon.core
import os


EDGE = 1

OUT = "out"
IN = "in"

RISING = "rising"
FALLING = "falling"
BOTH = "both"

PULLDOWN = "pulldown"
PULLUP = "pullup"

GPIO_DIR = "/sys/class/gpio/"


class PinAPI(object):
    def __init__(self, pin_num):
        self.pin_num = pin_num

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    value = property(lambda p: p.get(),
                     lambda p, v: p.set(v),
                     doc="The value of the pin: 1 if the pin is high, 0 if "
                         "the pin is low.")


class Pin(PinAPI):
    """Controls a GPIO pin."""

    __trigger__ = EDGE

    def __init__(self, pin_num, direction=IN, interrupt=None,
                 pull=None):
        """Creates a pin

        Parameters:
        pin_num  -- the pin on the header to control.
        direction       -- (optional) the direction of the pin,
                           either IN or OUT.
        interrupt       -- (optional)
        pull            -- (optional)

        Raises:
        IOError        -- could not export the pin (if direction is given)
        """
        super(Pin, self).__init__(pin_num)
        self._file = None
        self._direction = direction
        self._interrupt = interrupt
        self._pull = pull

    def open(self):
        export(self.pin_num)
        microstackcommon.core.wait_until_access(self._pin_path("value"),
                                                access=os.W_OK,
                                                timeout=1)
        self._file = open(self._pin_path("value"), "r+")
        self._write("direction", self._direction)
        if self._direction == IN:
            self._write("edge",
                        self._interrupt
                        if self._interrupt is not None else "none")

    def close(self):
        if not self.closed:
            if self.direction == OUT:
                self.value = 0
            self._file.close()
            self._file = None
            self._write("direction", IN)
            self._write("edge", "none")
            unexport(self.pin_num)

    def get(self):
        """The current value of the pin: 1 if the pin is high or 0 if the pin
        is low.

        The value can only be set if the pin's direction is OUT.

        Raises:
        IOError -- could not read or write the pin's value.
        """
        self._check_open()
        self._file.seek(0)
        v = self._file.read()
        return int(v) if v else 0

    def set(self, new_value):
        self._check_open()
        if self._direction != OUT:
            raise ValueError("not an output pin")
        self._file.seek(0)
        self._file.write(str(int(new_value)))
        self._file.flush()

    @property
    def direction(self):
        """The direction of the pin: either IN or OUT.

        The value of the pin can only be set if its direction is OUT.

        Raises:
        IOError -- could not set the pin's direction.
        """
        return self._direction

    @direction.setter
    def direction(self, new_value):
        self._write("direction", new_value)
        self._direction = new_value

    @property
    def interrupt(self):
        """The interrupt property specifies what event (if any) will raise
        an interrupt.

        One of:
        Rising  -- voltage changing from low to high
        Falling -- voltage changing from high to low
        Both    -- voltage changing in either direction
        None    -- interrupts are not raised

        Raises:
        IOError -- could not read or set the pin's interrupt trigger
        """
        return self._interrupt

    @interrupt.setter
    def interrupt(self, new_value):
        self._write("edge", new_value)
        self._interrupt = new_value

    @property
    def pull(self):
        return self._pull

    def fileno(self):
        """Return the underlying file descriptor.  Useful for select, epoll,
        etc.
        """
        return self._file.fileno()

    @property
    def closed(self):
        """Returns if this pin is closed"""
        return self._file is None or self._file.closed

    def _check_open(self):
        if self.closed:
            raise IOError(str(self) + " is closed")

    def _write(self, filename, value):
        with open(self._pin_path(filename), "w+") as f:
            f.write(value)

    def _pin_path(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.pin_num, filename)

    def __repr__(self):
        return self.__module__ + "." + str(self)

    def __str__(self):
        return "{type}({pin_num})".format(
            type=self.__class__.__name__,
            pin_num=self.pin_num)


def export(pin_num):
    cmd = "echo {pin_num} > {gpio_dir}export".format(pin_num=pin_num,
                                                     gpio_dir=GPIO_DIR)
    subprocess.call([cmd], shell=True)


def unexport(pin_num):
    cmd = "echo {pin_num} > {gpio_dir}unexport".format(pin_num=pin_num,
                                                       gpio_dir=GPIO_DIR)
    subprocess.call([cmd], shell=True)
