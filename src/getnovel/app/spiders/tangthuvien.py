"""Get novel on domain tangthuvien.

.. _Web site:
   https://truyen.tangthuvien.vn

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TangThuVienSpider(Spider):
    """Define spider for domain: tangthuvien"""

    name = "tangthuvien"

    def __init__(
        self,
        url: str,
        start_chap: int,
        stop_chap: int,
        *args,
        **kwargs,
    ):
        """Initialize attributes.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling at this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.toc = []
        self.toc_len = 0

    def parse(self, response: Response):
        """Extract info and send request to table of content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to table of content.
        """
        yield get_info(response)
        uid = response.xpath('//*[@name="book_detail"]/@content').get()
        yield response.follow(
            url=f"/story/chapters?story_id={uid}",
            callback=self.parse_start,
        )

    def parse_start(self, response: Response):
        """Extract link of the start chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter.
        """
        self.toc.extend(response.xpath("//a/@href").getall())
        self.toc_len = len(self.toc)
        yield Request(
            url=self.toc[self.start_chap - 1],
            meta={"id": self.start_chap},
            callback=self.parse_content,
        )

    def parse_content(self, response: Response):
        """Extract content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Chapter
            Chapter item.
        Request
            Request to the next chapter.
        """
        yield get_content(response)
        if (response.meta["id"] == self.toc_len) or (
            response.meta["id"] == self.stop_chap
        ):
            raise CloseSpider(reason="Done")
        yield Request(
            url=self.toc[response.meta["id"]],
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response) -> Info:
    """Get novel information.

    Parameters
    ----------
    response : Response
        The response to parse.

    Returns
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", "//div[5]//h1/text()")
    r.add_xpath("author", "//div[5]//div[2]/p[1]/a[1]/text()")
    r.add_xpath("types", "//div[5]//div[2]/p[1]/a[2]/text()")
    r.add_xpath("foreword", '//div[@class="book-intro"]/p/text()')
    r.add_xpath("image_urls", '//*[@id="bookImg"]/img/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    response : Response
        The response to parse.

    Returns
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=response)
    r.add_xpath("title", "//div[5]//h2/text()")
    r.add_xpath("content", '//div[contains(@class,"box-chap")]//text()')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
