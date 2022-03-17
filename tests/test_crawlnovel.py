"""Test the NovelCrawler class."""
import unittest
from pathlib import Path

from novelutils.utils.crawler import NovelCrawler


class MyTest(unittest.TestCase):
    def test_init(self):
        crawler = NovelCrawler(
            url=r'https://bachngocsach.com/reader/van-toc-chi-kiep-convert',
            raw_dir_path=Path('./raw_dir')
        )
        crawler.crawl(rm_raw=True, start_chap=1, stop_chap=2)
        self.assertEqual(len(list(Path('./raw_dir').glob('*'))), 4)
