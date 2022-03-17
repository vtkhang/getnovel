""" Test file cleaner."""
import unittest
from pathlib import Path

from novelutils.utils.file import FileConverter


class MyTest(unittest.TestCase):
    def test_init(self):
        a = FileConverter('./raw_dir', './result_dir')
        self.assertEqual(a.x, Path('./raw_dir'))
        self.assertEqual(a.y, Path('./result_dir'))

    def test_init_1(self):
        a = FileConverter('./raw_dir', None)
        self.assertEqual(a.y, Path('./result_dir'))

    def test_clean(self):
        a = FileConverter('./raw_dir', './txt_dir')
        a.clean(duplicate_chapter=True, rm_result=True)
        # https://stackoverflow.com/a/43430592
        self.assertEqual(len(list(Path('./raw_dir').glob('*'))), len(list(Path('./txt_dir').glob('*'))))

    def test_convert(self):
        a = FileConverter('./raw_dir', './xhtml_dir')
        a.convert_to_xhtml(duplicate_chapter=True, rm_result=True, lang_code='vi')
        self.assertEqual(len(list(Path('./raw_dir').glob('*'))), len(list(Path('./xhtml_dir').glob('*'))))
