"""
This module contains exceptions that can be generated by stores.
"""


class NotFoundException(Exception):
    """
    Indicates that an object or container could not be found.

    Check the error message for more detailed information.
    """

    def __init__(self, value='Nothing matching the key value was found in the store'):
        self.value = value

    def __str__(self):
        return repr(self.value)
