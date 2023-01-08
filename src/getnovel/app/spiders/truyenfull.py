"""Get novel on domain truyenfull.

.. _Web site:
   https://truyenfull.vn

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class TruyenFullSpider(Spider):
    """Define spider for domain: truyenfull"""

    name = "truyenfull"

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

    def parse(self, res: Response, *args, **kwargs):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(res)
        yield res.follow(
            url=f"chuong-{self.sa}/",
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self, res: Response):
        """Extract content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Chapter
            Chapter item.

        Request
            Request to the next chapter.
        """
        yield get_content(res)
        neu = res.xpath('//a[@id="next_chap"]/@href').get()
        if ("h" not in neu) or (res.meta["id"] == self.so):
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

    Returns
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=res)
    r.add_xpath("title", '//h3[@class="title"]/text()')
    r.add_xpath("author", '//div[@class="info"]/div[1]/a/text()')
    r.add_xpath("types", '//div[@class="info"]/div[2]/a/text()')
    r.add_xpath("foreword", '//div[@itemprop="description"]//text()')
    r.add_xpath("image_urls", '//div[@class="book"]/img/@src')
    r.add_value("url", res.request.url)
    return r.load_item()


def get_content(res: Response) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=res)
    r.add_value("id", str(res.meta["id"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath(
        "content",
        '//div[@id="chapter-c"]//text()[parent::i or parent::div or parent::p'
        ' and not(ancestor::div[contains(@class, "ads-network")])]',
    )
    return r.load_item()
