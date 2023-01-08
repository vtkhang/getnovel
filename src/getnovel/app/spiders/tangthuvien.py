"""Get novel on domain tangthuvien.

.. _Web site:
   https://truyen.tangthuvien.vn

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response, Request

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class TangThuVienSpider(Spider):
    """Define spider for domain: tangthuvien"""

    name = "tangthuvien"

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
        self.t = []  # table of content
        self.n = 0  # total chapters

    def parse(self, res: Response, *args, **kwargs):
        """Extract info and send request to the table of content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to the table of content.
        """
        yield get_info(res)
        uid = res.xpath('//*[@name="book_detail"]/@content').get()
        yield res.follow(
            url=f"/story/chapters?story_id={uid}",
            callback=self.parse_toc,
        )

    def parse_toc(self, res: Response):
        """Extract link of the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter.
        """
        self.t.extend(res.xpath("//a/@href").getall())
        self.n = len(self.t)
        yield Request(
            url=self.t[self.sa - 1],
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
        if (res.meta["id"] >= self.n) or (res.meta["id"] == self.so):
            raise CloseSpider(reason="done")
        yield Request(
            url=self.t[res.meta["id"]],
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
    r.add_xpath("title", "//div[5]//h1/text()")
    r.add_xpath("author", "//div[5]//div[2]/p[1]/a[1]/text()")
    r.add_xpath("types", "//div[5]//div[2]/p[1]/a[2]/text()")
    r.add_xpath("foreword", '//div[@class="book-intro"]/p/text()')
    r.add_xpath("image_urls", '//*[@id="bookImg"]/img/@src')
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
    r.add_xpath("title", "//div[5]//h2/text()")
    r.add_xpath("content", '//div[contains(@class,"box-chap")]//text()')
    return r.load_item()
