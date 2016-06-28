import time
import sys


class ChannelOrder:
    RGB = 0, 1, 2
    RBG = 0, 2, 1
    GRB = 1, 0, 2
    GBR = 1, 2, 0
    BRG = 2, 0, 1
    BGR = 2, 1, 0

    ORDERS = RGB, RBG, GRB, GBR, BRG, BGR


class DriverBase(object):
    """Base driver class to build other drivers from"""

    def __init__(self, num=0, width=0, height=0, c_order=ChannelOrder.RGB, gamma=None):
        if num == 0:
            num = width * height
            if num == 0:
                raise ValueError(
                    "Either num or width and height must be provided!")

        self.numLEDs = num
        self.gamma = gamma or range(256)

        self.c_order = c_order
        self.perm = ChannelOrder.ORDERS.index(c_order)

        self.width = width
        self.height = height
        self._buf = bytearray(self.bufByteCount())

        self._thread = None
        self.lastUpdate = 0

        if 'timedata' in sys.modules:
            self._flatten = self._flatten_timedata
        else:
            self._flatten = self._flatten_basic

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def cleanup(self):
        return self.__exit__(None, None, None)

    def bufByteCount(self):
        return 3 * self.numLEDs

    # Push new data to strand
    def _receive_colors(self, colors):
        # TODO: use abc here.
        raise RuntimeError("Base class receive_colors() called.")

    def receive_colors(self, colors, pos):
        start = time.time() * 1000.0
        self._receive_colors(colors[pos:self.numLEDs+pos])
        if self._thread:
            self.lastUpdate = (time.time() * 1000.0) - start

    def setMasterBrightness(self, brightness):
        return False

    # call _flatten() instead!
    def _flatten_basic(self, colors):
        return [i for c in colors for i in c]

    # call _flatten() instead!
    def _flatten_timedata(self, colors):
        return [int(i) for i in self._flatten_basic(colors)]

    def _color_correct(self, colors):
        gamma, (r, g, b) = self.gamma, self.c_order
        for i in range(self.numLEDs):
            fix = lambda x: gamma[int(max(0, min(255, int(x))))]  # flake8: noqa
            colors[i] = (fix(colors[i][r]), fix(colors[i][g]), fix(colors[i][b]))
        return colors
