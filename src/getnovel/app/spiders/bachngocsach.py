"""Get novel on domain bachngocsach.

.. _Web site:
   https://bachngocsach.com.vn/reader

"""

from scrapy import Spider
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class BachNgocSachSpider(Spider):
    """Define spider for domain: bachngocsach"""

    name = "bachngocsach"

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
        yield response.follow(
            url=f"{response.url}/muc-luc?page=all", callback=self.parse_start
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
        try:
            yield response.follow(
                url=response.xpath(
                    f'(//*[@class="chuong-link"])[{self.start_chap}]'
                ).attrib["href"],
                meta={"id": self.start_chap},
                callback=self.parse_content,
            )
        except KeyError:
            self.logger.exception(msg="Start chap is not exist or xpath need to be fixed!")
            raise CloseSpider(reason="Stopped")

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
        next_url = response.xpath('//a[contains(@class,"page-next")]').attrib["href"]
        if (not next_url) or (response.meta["id"] == self.stop_chap):
            raise CloseSpider(reason="Done")
        yield response.follow(
            url=next_url,
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
    r.add_xpath("title", '//*[@id="truyen-title"]/text()')
    r.add_xpath("author", '//div[@id="tacgia"]/a/text()')
    r.add_xpath("types", '//div[@id="theloai"]/a/text()')
    r.add_xpath("foreword", '//div[@id="gioithieu"]/div/p/text()')
    r.add_xpath("image_urls", '//div[@id="anhbia"]/img/@src')
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
    r.add_xpath("title", '//h1[@id="chuong-title"]/text()')
    r.add_xpath(
        "content",
        '//div[@id="noi-dung"]/p/text()',
    )
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
