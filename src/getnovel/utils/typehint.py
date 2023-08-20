"""Type hint for getnovel."""
from pathlib import Path

# Don't need to check types in python. If the code fail,
# it will raise exception -> handle exception is enough.
# https://stackoverflow.com/a/602078
# Path object which can be string or pathlib.Path
PathStr = Path | str
DictPath = dict[int, Path]  # Dict object which key type int and value type pathlib.Path
ListPath = list[Path]  # List path
ListStr = list[str]  # List string
