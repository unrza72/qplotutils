

class Configuration:

    __shared_state = None

    def __init__(self):
        if not Configuration.__shared_state:
            Configuration.__shared_state = self.__dict__

            self.__debug = False

        else:
            self.__dict__ = Configuration.__shared_state

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = value