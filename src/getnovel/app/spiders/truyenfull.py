"""Get novel from domain truyenfull.

.. _Web site:
   https://truyenfull.vn

"""

from pathlib import Path

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenFullSpider(Spider):
    """Declare spider for domain: truyenfull"""

    name = "truyenfull"

    def __init__(
        self,
        url: str,
        start_chap: int,
        stop_chap: int,
        save_path: Path,
        *args,
        **kwargs,
    ):
        """Initialize attributes.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        save_path : Path
            Path of raw directory.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling from this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.save_path = save_path

    def parse(self, response: Response):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(response)
        yield Request(
            url=f"{response.url}chuong-{self.start_chap}/",
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
        Request
            Chapter item.
        Request
            Request to the next chapter.
        """
        yield get_content(response)
        next_url = response.xpath('//a[@id="next_chap"]/@href').get()
        if (next_url == "javascript:void(0)") or response.meta["id"] == self.stop_chap:
            raise CloseSpider(reason="Done")
        yield Request(
            url=next_url,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response):
    """Get novel information.

    Parameters
    ----------
    response : Response
        The response to parse.
    """
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//h3[@class="title"]/text()')
    r.add_xpath("author", '//div[@class="info"]/div[1]/a/text()')
    r.add_xpath("types", '//div[@class="info"]/div[2]/a/text()')
    r.add_xpath("foreword", '//div[@itemprop="description"]//text()')
    r.add_xpath("image_urls", '//div[@class="book"]/img/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response):
    """Get chapter content.

    Parameters
    ----------
    response : Response
        The response to parse.
    """
    r = ChapterLoader(item=Chapter(), response=response)
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath(
        "content",
        '//div[@id="chapter-c"]//text()[parent::i or parent::div or parent::p'
        ' and not(ancestor::div[contains(@class, "ads-network")])]',
    )
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
