class NotFoundException(Exception):
    def __init__(self, value='Nothing matching the key value was found in the store'):
        self.value = value

    def __str__(self):
        return repr(self.value)
