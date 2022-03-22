"""Define NovelCrawler class."""
import re
import urllib
import logging
import unicodedata

from pathlib import Path
from distutils.dir_util import remove_tree

from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader

from novelutils.utils.file import FileConverter
from novelutils.utils.typehint import PathStr, ListPath

_logger = logging.getLogger(__name__)


class NovelCrawler:
    """Download novel from website."""

    def __init__(self, url: str, raw_dir_path: PathStr = None) -> None:
        """Initialize NovelCrawler with url.

        Args:
            url: full web site to novel info page
            raw_dir_path: path to raw directory (default: None)
        """
        validate_url(url)
        self.u: str = url
        self.x: Path = Path()
        if raw_dir_path is None:
            tmp: list = self.u.split("/")
            tmp_1: str = tmp[-1]
            if tmp_1 == "":
                for item in reversed(tmp):
                    if item != "":
                        tmp_1 = item
                        break
            self.x = Path.cwd() / tmp_1 / "raw_dir"
        else:
            self.x = Path(raw_dir_path)
        self.x.mkdir(parents=True, exist_ok=True)
        self.f: ListPath = list()  # list of crawled files

    def crawl(
        self, rm_raw: bool, start_chap: int, stop_chap: int, clean: bool = True
    ) -> None:
        """Start crawling and clean result.

        Args:
            rm_raw: if specified, remove all old files in raw directory
            start_chap: start chapter index
            stop_chap: stop chapter index, input -1 to get all chapters
            clean: if specified, not auto clean text after crawling
        Returns:
            None
        """
        if start_chap is None:
            raise CrawlNovelError("Missing start chapter index")
        if stop_chap is None:
            raise CrawlNovelError("Missing stop chapter index")
        if start_chap < 1:
            raise CrawlNovelError("Index of start chapter need to be greater than zero")
        if stop_chap < start_chap and stop_chap != -1:
            raise CrawlNovelError(
                "Index of stop chapter need to be greater than start chapter or equal -1"
            )
        if rm_raw is True:
            _logger.info("Remove existing files in: %s", self.x.resolve())
            self._rm_raw()
        spider_class = self._get_spider()
        process = CrawlerProcess(
            settings={
                "AUTOTHROTTLE_ENABLED": True,
                "DEFAULT_REQUEST_HEADERS": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/84.0.4147.105 Safari/537.36",
                },
                "LOG_FORMAT": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                "LOG_SHORT_NAMES": True,
            }
        )
        process.crawl(
            spider_class,
            url=self.u,
            save_path=self.x,
            start_chap=start_chap,
            stop_chap=stop_chap,
        )
        process.start()
        _logger.info("Done crawling. View result at: %s", str(self.x.resolve()))
        _logger.info("Start cleaning.")
        if clean is True:
            c = FileConverter(self.x, self.x)
            c.clean(duplicate_chapter=False, rm_result=False)
            self.f: ListPath = list(c.get_file_list(ext="txt"))

    def _get_spider_name(self) -> str:
        """Return the spider name base on url input.

        bachngocsach, sstruyen, tangthuvien, truyencv, truyendkm, truyenfull, webtruyen is VI
        ptwxz, uukanshu is ZH
        metruyenchu, vtruyen, nuhiep use spider truyencv_sub (Blocked by cloudflare)

        Returns:
            str: spider name
        """
        spider_name = ""
        spider_name_list = (
            "bachngocsach",
            "sstruyen",
            "tangthuvien",
            "truyencv",
            "truyendkm",
            "truyenfull",
            "webtruyen",
            "metruyenchu",
            "vtruyen",
            "nuhiep",
            "truyenchu",
            "ptwxz",
            "uukanshu",
            "69shu",
            "twpiaotian",
        )
        for item in spider_name_list:
            if item in self.u:
                spider_name = item
        if spider_name == "":
            raise CrawlNovelError("Can't find spider name!")
        if spider_name in ("metruyenchu", "vtruyen", "nuhiep"):
            return "truyencv_sub"
        return spider_name

    def _get_spider(self):
        """Get spider class from the url.

        Returns:
            an instance of spider class
        """
        spider_name = self._get_spider_name()
        loader = SpiderLoader.from_settings(
            Settings({"SPIDER_MODULES": ["novelutils.app.spiders"]})
        )
        if spider_name not in loader.list():
            raise CrawlNovelError(f"Spider {spider_name} not found!")
        return loader.load(spider_name)

    def _update_chapter_list(self) -> None:
        """Update the chapter list if any file is removed.

        Returns:
            None
        """
        temp: ListPath = list()
        for item in self.f:
            if item.exists():
                temp.append(item)
        del self.f
        self.f: ListPath = temp

    def _rm_raw(self) -> None:
        """Remove old files in raw directory.

        Returns:
            None
        """
        if any(self.x.iterdir()):
            remove_tree(str(self.x))
            self.x.mkdir()

    def get_raw(self) -> Path:
        """Return the path to raw directory."""
        return self.x

    def get_chapters(self) -> tuple:
        """Return the list of chapters."""
        self._update_chapter_list()
        return tuple(self.f)

    def get_langcode(self) -> str:
        """Return language code of novel."""
        if self._get_spider_name() in ("ptwxz", "uukanshu", "69shu", "twpiaotian"):
            return "zh"
        else:
            return "vi"


class CrawlNovelError(Exception):
    """Handle NovelCrawler Exception."""

    pass


# Using this answer from stackoverflow:https://stackoverflow.com/a/55827638
# Check https://regex101.com/r/A326u1/5 for reference
DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
    # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"(?:(?:(?=\S{0,253}(?:$|:))"
    # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
    r"|localhost)"  # accept also "localhost" only
    r"(:\d{1,5})?",  # port [optional]
    re.IGNORECASE,
)
SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$", re.IGNORECASE  # scheme: http(s) or ftp(s)
)


def validate_url(url: str):
    """Validator for the url value.

    Args:
        url (str): string url

    Raises:
        CrawlNovelError: No URL specified
        CrawlNovelError: URL exceeds its maximum length of 2048 characters
        CrawlNovelError: No URL scheme specified
        CrawlNovelError: URL scheme must either be http(s) or ftp(s)
        CrawlNovelError: No URL domain specified
        CrawlNovelError: URL domain malformed

    Returns:
        str: string url if it pass the validator
    """
    url = url.strip()

    if url is None:
        raise CrawlNovelError("No URL specified")

    if len(url) > 2048:
        raise CrawlNovelError(
            f"URL exceeds its maximum length of 2048 characters (given length={len(url)})"
        )

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        raise CrawlNovelError("No URL scheme specified")

    if not re.fullmatch(SCHEME_FORMAT, scheme):
        raise CrawlNovelError(
            f"URL scheme must either be http(s) or ftp(s) (given scheme={scheme})"
        )

    if not domain:
        raise CrawlNovelError("No URL domain specified")

    if not re.fullmatch(DOMAIN_FORMAT, domain):
        raise CrawlNovelError(f"URL domain malformed (domain={domain})")


# using the answer from https://stackoverflow.com/a/295466
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
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
    return re.sub(r"[-\s]+", "-", value).strip("-_")[0:255]


if __name__ == "__main__":
    test_str = "Giang Hồ Kỳ Lục Công - 江湖奇功录"

    print(test_str)
    r_str = slugify(test_str, allow_unicode=True)
    print(r_str)
