"""Get novel from domain metruyencv

.. _Web sites:
   https://metruyencv.com

"""
from pathlib import Path

import scrapy
from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class MeTruyenCVSpider(scrapy.Spider):
    """Define spider for domain: metruyencv"""

    name = "metruyencv"

    def __init__(
        self,
        url: str,
        save_path: Path,
        start_chap: int,
        stop_chap: int,
        *args,
        **kwargs,
    ):
        """Initialize the attributes for this spider

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
        self.save_path = save_path
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.total_chapter = 0
        self.base_url = None

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the
        table of content (toc)

        Parameters
        ----------
        response : Response
            The response to parse

        Yields
        ------
        Request
            Request to the cover image page and toc page
        """
        yield get_info(response)
        total_chapter_str = response.xpath(
            '//*[@id="nav-tab-chap"]/span[2]/text()'
        ).get()
        if total_chapter_str is None:
            raise scrapy.exceptions.CloseSpider(
                reason="Couldn't get total chapter number"
            )
        try:
            total_chapter = int(total_chapter_str)
        except ValueError as e:
            raise scrapy.exceptions.CloseSpider(
                reason="Couldn't convert total chapter number to integer"
            ) from e
        self.base_url = response.request.url
        self.total_chapter = total_chapter
        yield scrapy.Request(
            url=self.base_url + r"/chuong-" + str(self.start_chap),
            meta={"id": self.start_chap},
            callback=self.parse_content,
        )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter

        Parameters
        ----------
        response : Response
            The response to parse

        Yields
        ------
        Request
            Request to the next chapter
        """
        yield get_content(response)
        if (
            response.meta["id"] >= self.total_chapter
            or response.meta["id"] == self.stop_chap
        ):
            raise scrapy.exceptions.CloseSpider(reason="Done")

        yield scrapy.Request(
            url=self.base_url + r"/chuong-" + str(response.meta["id"] + 1),
            headers=response.headers,
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
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//h1[@class="h3 mr-2"]/a/text()')
    r.add_xpath("author", '//ul[@class="list-unstyled mb-4"]/li[1]/a/text()')
    r.add_xpath("types", '//ul[@class="list-unstyled mb-4"]/li[position()>1]/a/text()')
    r.add_xpath("foreword", '//div[@class="content"]/p/text()')
    r.add_xpath("image_urls", '//div[@class="media"]//img[1]/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: scrapy.http.Response):
    """Get content of this novel

    Parameters
    ----------
    response : Response
        The response to parse
    """
    r = ChapterLoader(item=Chapter(), response=response)
    r.add_xpath("title", '//div[contains(@class,"nh-read__title")]/text()')
    r.add_xpath("content", '//div[@id="article"]/text()')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
