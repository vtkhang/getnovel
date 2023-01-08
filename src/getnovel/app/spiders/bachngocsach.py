"""Get novel on domain bachngocsach.

.. _Web site:
   https://bachngocsach.com.vn/reader

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response, Request

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class BachNgocSachSpider(Spider):
    """Define spider for domain: bachngocsach"""

    name = "bachngocsach"

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
        super().parse(*args, **kwargs)
        yield get_info(res)
        yield Request(
            url=f"{res.url}/muc-luc?page=all",
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
        yield res.follow(
            url=res.xpath(f'(//*[@class="chuong-link"]/@href)[{self.sa}]').get(),
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
        neu = res.xpath('//a[contains(@class,"page-next")]/@href').get()
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
    r.add_value("id", str(res.meta["id"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//h1[@id="chuong-title"]/text()')
    r.add_xpath("content", '//div[@id="noi-dung"]/p/text()')
    return r.load_item()
