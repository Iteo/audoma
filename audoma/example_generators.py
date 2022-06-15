import random

import lorem


def generate_lorem_ipsum(min_length=20, max_length=80) -> str:
    """
    This function generates a random string of lorem ipsum text.
        Args:
            min_length (int): The minimum length of the string.
            max_length (int): The maximum length of the string.

        Returns:
            str: A random string of lorem ipsum text.
    """
    random_lorem = lorem.text()
    if len(random_lorem) < min_length:
        random_lorem += lorem.text()
    if max_length < 20:
        max_length = max_length
    else:
        max_length = max([min([80, max_length]), min_length])
    min_length = min([max([20, min_length]), max_length])

    return random_lorem[: random.randint(min_length, max_length)]
