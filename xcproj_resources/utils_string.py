from random import choice
from string import ascii_lowercase


def random_string(length: int = 10):
    return ''.join(choice(ascii_lowercase) for i in range(length))
