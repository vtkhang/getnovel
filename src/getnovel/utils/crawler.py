"""Define NovelCrawler class."""

import logging
from pathlib import Path
from shutil import rmtree

import tldextract
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader

from getnovel.data import scrapy_settings
from getnovel.utils.file import FileConverter

_logger = logging.getLogger(__name__)


SPIDER_LOADER = SpiderLoader.from_settings(
    {"SPIDER_MODULES": ["getnovel.app.spiders"]},
)


class NovelCrawler:
    """Download novel from website."""

    def __init__(self: "NovelCrawler", url: str) -> None:
        """Initialize NovelCrawler."""
        self.url = url
        self.spider = None
        self.result = None

    def crawl(
        self: "NovelCrawler",
        url: str,
        start: int,
        stop: int,
        **options: dict,
    ) -> None:
        """Download novel and store it in the raw directory.

        Parameters
        ----------
        url: str
            Url of the novel information page.
        start : int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        options: dict
            result:
                Path of result directory.
            rm:
                If specified, remove all existing files in result directory.
            clean:
                If specified, clean result files after crawling.

        Raises
        ------
        CrawlNovelError
            Index of start chapter need to be greater than zero.
        CrawlNovelError
            Start chapter need to be lesser than stop chapter if stop chapter is not -1.
        """
        if start < 1:
            msg = "Index of start index need to be greater than zero"
            raise CrawlNovelError(msg)
        if (start > stop) and (stop > -1):
            msg = "Start chapter need to be lesser than stop chapter"
            " if stop chapter is not -1."
            raise CrawlNovelError(msg)
        # Load spider
        spider_name = tldextract.extract(url).domain
        self.spider = SPIDER_LOADER.load(spider_name)
        # Resolve result directory
        self.result = self.__resolve_result(options.get("result", None))
        # remove existing files
        if options.get("rm", False) and self.result.exists():
            rmtree(self.result)
        self.result.mkdir(parents=True, exist_ok=True)
        # start crawling
        settings = scrapy_settings(self.result)
        process = CrawlerProcess(settings)
        process.crawl(self.spider, url=url, start=start, stop=stop)
        process.start()
        _logger.info("Done crawling. View result at: %s", self.result)
        # clean result
        if options.get("clean", False) is True:
            _logger.info("Start cleaning")
            c = FileConverter(self.result, self.result)
            c.clean(dedup=False, rm=False)

    def __resolve_result(self: "NovelCrawler", result: Path | None) -> Path:
        """Resolve result directory."""
        if result is None:
            result = Path.cwd()
            title_pos = self.spider.title_pos
            splitted_url = self.url.split("/")
            if title_pos:
                result = result / splitted_url[title_pos]
            else:
                result = result / f"{self.spider.name}-{splitted_url[-1]}"
        return result.resolve()


class CrawlNovelError(Exception):
    """Handle NovelCrawler Exception."""
