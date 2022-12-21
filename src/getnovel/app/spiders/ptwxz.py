"""Get novel from domain ptwxz.

.. _Web site:
   https://www.ptwxz.com

"""

from pathlib import Path

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class PtwxzSpider(Spider):
    """Define spider for domain: ptwxz"""

    name = "ptwxz"

    def __init__(
        self,
        url: str,
        save_path: Path,
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
        self.total_chap = 0

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
        toc_url = response.xpath('//*[@id="content"]//a[1]/@href').get()
        yield Request(url=f"https://www.ptwxz.com{toc_url}", callback=self.parse_start)

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
        chapter_links = response.xpath('//div[@class="centent"]//@href').getall()
        self.total_chap = len(chapter_links)
        if self.start_chap > self.total_chap:
            raise CloseSpider(reason="Start chapter is greater than total chap!")
        chapter = chapter_links[self.start_chap - 1]
        yield Request(
            url=response.urljoin(chapter),
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
        next_url = response.xpath("//div[3]/a[3]/@href").get()
        if (response.meta["id"] == self.total_chap) or (
            response.meta["id"] == self.stop_chap
        ):
            raise CloseSpider(reason="Done")
        yield Request(
            url=response.urljoin(next_url),
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
    ihref = response.xpath('//*[@id="content"]//td[2]//img/@src').get()
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//*[@id="content"]//tr[1]//h1/text()')
    r.add_xpath("author", '//*[@id="content"]//tr[2]/td[2]/text()')
    r.add_xpath("types", '//*[@id="content"]//tr[2]/td[1]/text()')
    r.add_xpath("foreword", '//*[@id="content"]//td[2]//text()[4]')
    r.add_value("image_urls", response.urljoin(ihref))
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
    r.add_xpath("title", "//h1/text()")
    r.add_xpath("content", "//body/text()")
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
