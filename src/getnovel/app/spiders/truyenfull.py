"""Get novel from domain truyenfull

.. _Web site:
   https://truyenfull.vn

"""
from pathlib import Path
import scrapy
from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenFullReworkSpider(scrapy.Spider):
    """Define spider for domain: truyenfull"""

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
        """Initialize the attributes for spider

        Parameters
        ----------
        url : str
            The link of the novel information page
        save_path : Path
            Path of raw directory
        start_chap : int
            Start crawling from this chapter
        stop_chap : int
            Stop crawling from this chapter, input -1 to get all chapters
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.save_path = save_path

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and send request to start chapter

        Parameters
        ----------
        response : Response
            The response to parse

        Yields
        ------
        Request
            Request to the start chapter
        """
        yield get_info(response=response)
        yield scrapy.Request(
            url=f"{response.url}chuong-{self.start_chap}/",
            meta={"id": self.start_chap},
            callback=self.parse_content,
        )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter and send request to next chapter

        Parameters
        ----------
        response : Response
            The response to parse

        Yields
        ------
        Request
            Request to the next chapter
        """
        yield get_content(response=response)
        link_next_chap = response.xpath('//a[@id="next_chap"]/@href').getall()[0]
        if (link_next_chap == "javascript:void(0)") or response.meta[
            "id"
        ] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
        yield scrapy.Request(
            url=link_next_chap,
            headers=response.request.headers,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: scrapy.http.Response):
    """Get info of this novel

    Parameters
    ----------
    response : Response
        The response to parse
    """
    # extract info
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//h3[@class="title"]/text()')
    r.add_xpath("author", '//div[@class="info"]/div[1]/a/text()')
    r.add_xpath("types", '//div[@class="info"]/div[2]/a/text()')
    r.add_xpath("foreword", '//div[@itemprop="description"]//text()')
    r.add_xpath("image_urls", '//div[@class="book"]/img/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: scrapy.http.Response):
    """Get content of this novel

    Parameters
    ----------
    response : Response
        The response to parse
    save_path : Path
        Path of raw directory
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
