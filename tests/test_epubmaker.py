"""Test epub.py module"""
from pathlib import Path

from novelutils.utils.epub import EpubMaker

e = EpubMaker(output='./result_dir')
e.from_raw(raw_dir_path=Path('./raw_dir'), lang_code='vi', duplicate_chapter=True)
