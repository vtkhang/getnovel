"""Get novel on domain sstruyen.

.. _Web site:
   https://sstruyen.vn/

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class SSTruyenSpider(Spider):
    """Define spider for domain: sstruyen.

    Attributes:
    ----------
    name : str
        Name of the spider.
    start_urls : list
        List of url to start crawling from.
    sa : int
        The chapter index to start crawling.
    so : int
        The chapter index to stop crawling after that.
    c : str
        Language code of novel.
    """

    name = "sstruyen"

    def __init__(self, u: str, start: int, stop: int, *args, **kwargs):
        """Initialize attributes.

        Parameters
        ----------
        u : str
            Url of the novel information page.
        start: int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u]
        self.sa = int(start)
        self.so = int(stop)
        self.c = "vi"  # language code

    def parse(self, res: Response):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields:
        ------
        Info
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(res)
        yield res.follow(
            url=f"chuong-{self.sa}/",
            callback=self.parse_content,
            meta={"id": self.sa},
        )

    def parse_content(self, res: Response):
        """Extract content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields:
        ------
        Chapter
            Chapter item.

        Request
            Request to the next chapter.
        """
        yield get_content(res)
        neu = res.xpath('//*[@id="j_content"]/div[3]//li[@class="next"]/a/@href').get()
        if (neu is None) or (res.meta["id"] == self.so):
            raise CloseSpider(reason="done")
        yield res.follow(
            url=neu,
            meta={"id": res.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(res: Response) -> Info:
    """Get novel information.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns:
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=res)
    r.add_xpath("title", "//div[5]//h1//text()")
    r.add_xpath("author", '//*[@itemprop="author"]/text()')
    r.add_xpath("types", "//div[5]//div[2]/div[3]//p[2]/a/text()")
    r.add_xpath("foreword", "//div[5]//div[3]/p/text()")
    r.add_xpath("image_urls", "//div[5]//div[1]/img/@src")
    r.add_value("url", res.request.url)
    return r.load_item()


def get_content(res: Response) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns:
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=res)
    r.add_value("id", str(res.meta["id"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//*[@id="j_content"]//h2//text()')
    r.add_xpath("content", '//*[@id="j_content"]//p/text()')
    return r.load_item()
