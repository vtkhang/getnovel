"""Get novel on domain dtruyen.

.. _Web site:
   https://dtruyen.com/

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.http.response.text import TextResponse
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenChuSpider(Spider):
    """Define spider for domain: truyenchu"""

    name = "dtruyen"

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
        # calculate the position of start_chap in menu list
        total_chap = 30
        start_chap = self.start_chap - 1
        menu_page_have_start_chap = start_chap // total_chap + 1
        pos_of_start_chap_in_menu = start_chap % total_chap + 1
        yield Request(
            url=f"{response.url}{menu_page_have_start_chap}/",
            meta={
                "pos_start": pos_of_start_chap_in_menu,
            },
            callback=self.parse_start,
        )

    def parse_start(self, response: TextResponse):
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
        yield Request(
            url=response.xpath(
                f'(//*[@id="chapters"]/ul//a)[{response.meta["pos_start"]}]'
            ).attrib["href"],
            callback=self.parse_content,
            meta={"id": self.start_chap},
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
        next_url = response.xpath('//*[@id="chapter"]/div[1]/a[4]').attrib["href"]
        if (next_url == "#") or (response.meta["id"] == self.stop_chap):
            raise CloseSpider(reason="Done")
        yield Request(
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
    r.add_xpath("title", '//h1[@itemprop="name"]/text()')
    r.add_xpath("author", '//a[@itemprop="author"]/text()')
    r.add_xpath("types", '//a[@itemprop="genre"]/text()')
    r.add_xpath("foreword", '//*[@id="story-detail"]/div[2]/div[3]//text()')
    r.add_xpath("image_urls", '//*[@id="story-detail"]/div[1]/div[1]/img/@src')
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
    r.add_xpath("title", '//*[@id="chapter"]/header/h2/text()')
    r.add_xpath("content", '//*[@id="chapter-content"]/text()')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
