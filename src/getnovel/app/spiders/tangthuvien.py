"""Get novel on domain tangthuvien.

.. _Website:
   https://truyen.tangthuvien.vn

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class TangThuVienSpider(Spider):
    """Define spider for domain: tangthuvien.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "tangthuvien"
    title_pos = -1
    lang_code = "vi"

    def __init__(self: "TangThuVienSpider", url: str, start: int, stop: int) -> None:
        """Initialize attributes.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        start: int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        """
        self.start_urls = [url]
        self.sa = int(start)
        self.so = int(stop)
        self.t = []  # table of content
        self.n = 0  # total chapters

    def parse(self: "TangThuVienSpider", res: Response) -> None:
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

    def parse_toc(self: "TangThuVienSpider", res: Response) -> None:
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

    def parse_content(self: "TangThuVienSpider", res: Response) -> None:
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
