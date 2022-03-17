"""Test the argparse novelutils
"""
import sys
import unittest
from pathlib import Path

import novelutils


class ArgsParseTest(unittest.TestCase):
    def test_crawl(self):
        sys.argv = [
            'novelutils',
            'crawl',
            'https://truyen.tangthuvien.vn/doc-truyen/dich-day-la-tinh-cau-cua-ta-gia-thi-nga-tinh-cau',
            '--start',
            '2',
            '--stop',
            '5',
            '--raw_dir',
            str(Path('./raw_dir'))
        ]
        novelutils.main(sys.argv)
        _ = self

if __name__ == '__main__':
    a = ArgsParseTest()
    a.test_crawl()
