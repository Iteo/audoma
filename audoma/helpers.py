import random

import lorem


def generate_lorem_ipsum(min_length=20, max_length=80):
    random_lorem = lorem.text()
    max_length = max([min([max_length, 80]), max_length])
    min_length = max([min_length, 20])
    if min_length > max_length:
        min_length = max_length
    return random_lorem[: random.randint(min_length, max_length)]
