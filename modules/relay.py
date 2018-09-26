import sys
import time

mockup = False
try:
    import gpiozero
except ImportError:
    mockup = True
    print("No gpiozero, working with mockup relay")


class Relay:
    global mockup
    __pin = 0
    instance = False

    def __init__(self, pin):
        self.__pin = pin
        if mockup:
            self.instance = MockupRelay(self.__pin)
        else:
            self.instance = gpiozero.OutputDevice(self.__pin, active_high=False, initial_value=False)

    def set(self, on_off):
        if on_off:
            self.instance.on()
        else:
            self.instance.off()

    def on(self):
        self.set(True)

    def off(self):
        self.set(False)

    def toggle_relay():
        self.instance.toggle()


class MockupRelay:
    __pin = 0
    def __init__(self, pin):
        self.__pin = pin

    def on(self):
        print("On " + str(self.__pin))

    def off(self):
        print("Off " + str(self.__pin))

    def toggle():
        print("Toggle " + str(self.__pin))