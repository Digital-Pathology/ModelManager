
"""
    Utility functions for the model manager
"""

from curses.ascii import NL
from distutils.log import error
import io


import os
from typing import Any, Iterable, Iterator


def iterate_by_n(collection: Iterable[Any], n: int, yield_remainder: bool = False, error_if_remainder: bool = False) -> Iterator[Any]:
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
    nugget = []
    for item in collection:
        if len(nugget) == n:
            yield nugget
            nugget = []
        nugget.append(item)
    if len(nugget) == n:
        yield nugget
    else:
        if error_if_remainder:
            raise Exception(f"{len(nugget)} items left over")
        if yield_remainder:
            yield nugget


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
