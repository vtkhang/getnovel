"""Define NovelCrawler class."""

import logging
import json
import time
from pathlib import Path
from shutil import rmtree

import tldextract
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader

from getnovel.data import scrapy_settings
from getnovel.utils.file import FileConverter
from getnovel.utils.typehint import PathStr

_logger = logging.getLogger(__name__)


class NovelCrawler:
    """Download novel from website"""

    def __init__(self, url: str):
        """Initialize NovelCrawler with url, and assign path of raw
        directory.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        """
        self.u: str = url
        self.spn = tldextract.extract(self.u).domain  # spider name

    def crawl(
            self,
            rm: bool,
            start: int,
            stop: int,
            clean: bool,
            result: PathStr = None,
            custom_settings: PathStr = None,
    ) -> Path:
        """Download novel and store it in the raw directory.

        Parameters
        ----------
        rm : bool
            If specified, remove all existing files in result directory.
        start : int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        clean : bool
            If specified, clean result files after crawling.
        result : PathStr, optional
            Path of result directory, by default None.
        custom_settings: PathStr, optional
            Path of custom settings file, by default None.

        Raises
        ------
        CrawlNovelError
            Index of start chapter need to be greater than zero.
        CrawlNovelError
            Start chapter need to be lesser than stop chapter if stop chapter is not -1.

        Returns
        -------
        Path
            Path the raw directory.
        """
        if start < 1:
            raise CrawlNovelError("Index of start index need to be greater than zero")
        if (start > stop) and (stop > -1):
            raise CrawlNovelError(
                "Start chapter need to be lesser than stop chapter if stop chapter is not -1."
            )
        if result is None:
            rp = Path.cwd() / self.spn / time.strftime(r"%Y_%m_%d-%H_%M_%S") / "raw"
        else:
            rp = Path(result)
        if rm is True:
            _logger.info("Remove existing files in: %s", rp.resolve())
            if rp.exists():
                rmtree(rp)
        rp.mkdir(exist_ok=True, parents=True)
        rp = rp.resolve()
        spider_class = self._get_spider()
        settings = scrapy_settings.get_settings(result=rp)
        if custom_settings is not None:
            with Path(custom_settings).open(mode="r", encoding="utf-8") as cs:
                settings.update(json.load(cs))
                cs.close()
        cwd_settings = Path.cwd() / "settings.json"
        if cwd_settings.exists():
            with cwd_settings.open(mode="r", encoding="utf-8") as cws:
                settings.update(json.load(cws))
                cws.close()
        if settings['LOG_FILE'] is not None:
            print(f"> Please view log file at: {Path(settings['LOG_FILE']).resolve()}")
        process = CrawlerProcess(settings=settings)
        process.crawl(
            spider_class,
            u=self.u,
            start=start,
            stop=stop,
        )
        process.start()
        _logger.info("Done crawling. View result at: %s", rp)
        if clean is True:
            _logger.info("Start cleaning")
            c = FileConverter(rp, rp)
            c.clean(dedup=False, rm_result=False)
        return rp

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
            Settings({"SPIDER_MODULES": ["getnovel.app.spiders"]})
        )
        if self.spn not in loader.list():
            raise CrawlNovelError(f"Spider {self.spn} not found!")
        return loader.load(self.spn)

    def get_langcode(self) -> str:
        """Return language code of novel"""
        if self.spn in ("ptwxz", "uukanshu", "69shu"):
            return "zh"
        else:
            return "vi"


class CrawlNovelError(Exception):
    """Handle NovelCrawler Exception"""
