
import os
from typing import Iterable

def iterate_by_n(collection: Iterable, n: int, ignore_remainder=True):
    """ a generator function returning sets of n items from collection """
    i = 0
    while i+n <= len(collection):
        yield collection[i:i+n]
        i += n
    if not ignore_remainder and len(collection) % n != 0:
        print(collection)
        raise Exception(f"{len(collection) % n} items left over")

def open_file(filepath: str, binary: bool = True):
    """ opens a file with 'w' or 'x' based on whether the file exists"""
    file_exists = os.path.exists(filepath)
    open_mode = 'w' if file_exists else 'x'
    if binary: open_mode += 'b'
    return open(filepath, open_mode)
