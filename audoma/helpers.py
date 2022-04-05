import random

import lorem


def generate_lorem_ipsum(min_length=None, max_length=None):
    random_lorem = lorem.text()
    max_length = max_length if max_length and max_length <= 255 else 255
    min_length = min_length if min_length and min_length <= 255 else 1
    return random_lorem[: random.randint(min_length, max_length)]
