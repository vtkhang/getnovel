"""Type hint for getnovel"""
from pathlib import Path
from typing import Union, Dict, List

# Don't need to check types in python. If the code fail,
# it will raise exception -> handle exception is enough.
# https://stackoverflow.com/a/602078
# Path object which can be string or pathlib.Path
PathStr = Union[Path, str]
DictPath = Dict[int, Path]  # Dict object which key type int and value type pathlib.Path
ListPath = List[Path]  # List path
ListStr = List[str]  # List string
