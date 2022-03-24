"""Define NovelCrawler class."""

import re
import logging
from pathlib import Path
from shutil import rmtree

import tldextract
import validators
import unicodedata
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader

from novelutils.data import scrapy_settings
from novelutils.utils.file import FileConverter
from novelutils.utils.typehint import PathStr, ListPath

_logger = logging.getLogger(__name__)


class NovelCrawler:
    """Download novel from website."""

    def __init__(self, url: str, raw_dir_path: PathStr = None) -> None:
        """Initialize NovelCrawler with url, and assign path of raw
        directory.

        Parameters
        ----------
        url : str
            The link of the novel information page.
        raw_dir_path : PathStr, optional
            Path of raw directory, by default None.
        """
        if validators.url(url) is False:
            _logger.error("The input url not valid!")
            return
        self.u: str = url
        self.rdp = None
        if raw_dir_path is None:
            tmp: list = self.u.split("/")
            tmp_1: str = tmp[-1]
            if tmp_1 == "":
                for item in reversed(tmp):
                    if item != "":
                        tmp_1 = item
                        break
            self.rdp = Path.cwd() / tmp_1 / "raw"
        else:
            self.rdp = Path(raw_dir_path)
        self.spn = tldextract.extract(self.u).domain  # spider name
        self.f: ListPath = []  # list of crawled files

    def crawl(
        self, rm_raw: bool, start_chap: int, stop_chap: int, clean: bool = True
    ) -> PathStr:
        """Download novel and store it in the raw directory.

        Parameters
        ----------
        rm_raw : bool
            If specified, remove all existing files in raw directory.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling at this chapter.
        clean : bool, optional
            If specified, clean result files, by default True.

        Raises
        ------
        CrawlNovelError
            Index of start chapter need to be greater than zero.
        CrawlNovelError
            Index of stop chapter need to be greater than start chapter or equal -1

        Returns
        -------
        PathStr
            Path the raw directory.
        """
        if start_chap < 1:
            raise CrawlNovelError(
                "Index of start chapter need to be greater than zero."
            )
        if stop_chap < start_chap and stop_chap != -1:
            raise CrawlNovelError(
                "Index of stop chapter need to be "
                "greater than start chapter or equal -1."
            )
        if rm_raw is True:
            _logger.info("Remove existing files in: %s", self.rdp.resolve())
            self._rm_raw()
        self.rdp.mkdir(exist_ok=True, parents=True)
        spider_class = self._get_spider()
        process = CrawlerProcess(settings=scrapy_settings.get_settings())
        process.crawl(
            spider_class,
            url=self.u,
            save_path=self.rdp,
            start_chap=start_chap,
            stop_chap=stop_chap,
        )
        process.start()
        _logger.info("Done crawling. View result at: %s", str(self.rdp.resolve()))
        if clean is True:
            _logger.info("Start cleaning.")
            c = FileConverter(self.rdp, self.rdp)
            c.clean(duplicate_chapter=False, rm_result=False)
            self.f: ListPath = list(c.get_file_list(ext="txt"))
        return self.rdp

    def _get_spider(self):
        """Get spider class based on the url domain.

        Returns
        -------
        object
            The spider class object.

        Raises
        ------
        CrawlNovelError
            Spider not found.
        """
        loader = SpiderLoader.from_settings(
            Settings({"SPIDER_MODULES": ["novelutils.app.spiders"]})
        )
        if self.spn not in loader.list():
            raise CrawlNovelError(f"Spider {self.spn} not found!")
        return loader.load(self.spn)

    def _rm_raw(self) -> None:
        """Remove old files in raw directory.

        Returns:
            None
        """
        if self.rdp.exists() and self.rdp.is_dir():
            rmtree(self.rdp)

    def get_langcode(self) -> str:
        """Return language code of novel."""
        if self.spn in ("ptwxz", "uukanshu", "69shu", "twpiaotian"):
            return "zh"
        else:
            return "vi"


class CrawlNovelError(Exception):
    """Handle NovelCrawler Exception."""

    pass


def slugify(value, allow_unicode=False):
    """Convert string to valid filename.

    This code was taken from https://github.com/django/django/blob/main/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
