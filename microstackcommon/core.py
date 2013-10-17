import time
import os


class Timeout(Exception):
    pass


def wait_until_access(filename, access, timeout):
    """Wait until we have access to a file.

    :param filename: The name of the file to wait for.
    :type filename: string
    :param access: Access rights.
    :type access: (os.W_OK, os.R_OK, etc)
    :param timeout: Length of time to wait before giving up.
    :type timeout: int
    """
    # this is a bit hacky, there is probably a better way of doing this.
    time_limit = time.time() + timeout
    while time.time() < time_limit:
        if os.access(filename, access):
            return
    raise Timeout("Waiting too long for file permissions. (%s)" % filename)
