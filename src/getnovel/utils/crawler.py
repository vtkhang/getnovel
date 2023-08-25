"""Define NovelCrawler class."""

import logging
from pathlib import Path
from shutil import rmtree

import tldextract
from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader

from getnovel.data import scrapy_settings

_logger = logging.getLogger(__name__)


SPIDER_LOADER = SpiderLoader.from_settings(
    Settings({"SPIDER_MODULES": ["getnovel.app.spiders"]}),
)


class NovelCrawler:
    """Download novel from website."""

    def __init__(self: "NovelCrawler", url: str) -> None:
        """Initialize NovelCrawler.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        """
        self.url = url
        self.spider = get_spider(url)  # spider instance
        self.settings = scrapy_settings.get_settings()  # default setting

    def crawl(self: "NovelCrawler", start: int, stop: int, **options: dict) -> None:
        """Download novel and store it in the raw directory.

        Parameters
        ----------
        start : int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        options: dict
            result: Path | None
                Path of result directory.
            rm: bool
                If specified, remove all existing files in result directory.

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
        # resolve result directory
        result = self.__resolve_result(options.get("result"))
        self.settings["RESULT"] = str(result)
        self.settings["IMAGES_STORE"] = str(result)
        # remove existing files
        if options.get("rm") and result.exists():
            rmtree(result)
        result.mkdir(parents=True, exist_ok=True)
        # start crawling
        process = CrawlerProcess(self.settings)
        process.crawl(self.spider, self.url, start, stop)
        process.start()
        _logger.info("Done crawling. View result at: %s", result)

    def __resolve_result(self: "NovelCrawler", result: Path | None) -> Path:
        """
        Resolve the result path.

        Parameters
        ----------
        result : Path or None
            The result path to resolve.

        Returns
        -------
        Path
            The resolved result path.
        """
        if result is None:
            result = Path.cwd()
            splitted_url = self.url.split("/")
            if hasattr(self.spider, "title_pos"):
                result = result / splitted_url[self.spider.title_pos]
            else:
                result = result / f"{self.spider.name}-{splitted_url[-1]}"
        return (result / "raw").resolve()


def get_spider(url: str) -> type[Spider]:
    """Get the spider object associated with the given URL.

    Parameters
    ----------
    url : str
        The URL for which to get the spider object.

    Returns
    -------
    Spider
        The spider object associated with the given URL.
    """
    spider_name = tldextract.extract(url).domain
    return SPIDER_LOADER.load(spider_name)


class CrawlNovelError(Exception):
    """Handle NovelCrawler Exception."""
