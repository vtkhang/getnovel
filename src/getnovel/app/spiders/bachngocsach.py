"""Get novel on domain bachngocsach.

.. _Website:
   https://bachngocsach.com.vn/reader

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class BachNgocSachSpider(Spider):
    """Define spider for domain: bachngocsach.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "bachngocsach"
    title_pos = -1
    lang_code = "vi"

    def __init__(self: "BachNgocSachSpider", url: str, start: int, stop: int) -> None:
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

    def parse(self: "BachNgocSachSpider", res: Response) -> None:
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
        yield Request(
            url=f"{res.url}/muc-luc?page=all",
            callback=self.parse_toc,
        )

    def parse_toc(self: "BachNgocSachSpider", res: Response) -> None:
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
        yield res.follow(
            url=res.xpath(f'(//*[@class="chuong-link"]/@href)[{self.sa}]').get(),
            meta={"index": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self: "BachNgocSachSpider", res: Response) -> None:
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
        neu = res.xpath('//a[contains(@class,"page-next")]/@href').get()
        if (neu is None) or (res.meta["index"] == self.so):
            raise CloseSpider(reason="done")
        yield res.follow(
            url=neu,
            meta={"index": res.meta["index"] + 1},
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
    r.add_xpath("title", '//*[@id="truyen-title"]/text()')
    r.add_xpath("author", '//div[@id="tacgia"]/a/text()')
    r.add_xpath("types", '//div[@id="theloai"]/a/text()')
    r.add_xpath("foreword", '//div[@id="gioithieu"]/div/p/text()')
    r.add_xpath("image_urls", '//div[@id="anhbia"]/img/@src')
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
    r.add_value("index", str(res.meta["index"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//h1[@id="chuong-title"]/text()')
    r.add_xpath("content", '//div[@id="noi-dung"]/p/text()')
    return r.load_item()
