
"""
    Utility functions for the model manager
"""

import io


import os
from typing import Any, Iterable, Iterator


def iterate_by_n(collection: Iterable[Any], n: int, ignore_remainder: bool = True) -> Iterator[Any]:
    """
    iterate_by_n returns a generator function returning sets of n items from collection

    :param collection: the collection to iterate over
    :type collection: Iterable
    :param n: the step size
    :type n: int
    :param ignore_remainder: whether to ignore the last len(collection)%n items, defaults to True
    :type ignore_remainder: bool, optional
    :raises Exception: when there is a remainder and ignore_remainder=False
    :yield: a set of n contiguous items from collection
    :rtype: Iterator[Any]
    """
    i = 0
    while i+n <= len(collection):
        yield collection[i:i+n]
        i += n
    if not ignore_remainder and len(collection) % n != 0:
        print(collection)
        raise Exception(f"{len(collection) % n} items left over")


def open_file(filepath: str, binary: bool = True) -> io.TextIOWrapper:
    """
    open_file opens a file with 'w' or 'x' based on whether the file exists

    :param filepath: the file to be opened
    :type filepath: str
    :param binary: whether to open the file in binary mode, defaults to True
    :type binary: bool, optional
    :return: the opened file
    :rtype: io.TextIOWrapper
    """
    file_exists = os.path.exists(filepath)
    open_mode = 'w' if file_exists else 'x'
    if binary:
        open_mode += 'b'
    return open(filepath, open_mode)
