"""Get novel on domain 69shu.

.. _Web site:
   https://www.69shu.com

"""

from pathlib import Path

from scrapy import Spider
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class SixNineShuSpider(Spider):
    """Define spider for domain: 69shu"""

    name = "69shu"

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
            Stop crawling at this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.save_path = save_path
        self.total_chap = 0

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
            url=response.xpath("//div[3]//div[3]/a/@href").get(),
            callback=self.parse_start
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
        chapter_links = response.xpath('//*[@id="catalog"]//a/@href').getall()
        self.total_chap = len(chapter_links)
        if self.start_chap > self.total_chap:
            raise CloseSpider(
                reason="Start chapter index is greater than total chapters"
            )
        yield response.follow(
            url=chapter_links[self.start_chap - 1],
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
        next_url = response.xpath("//div[3]//a[4]/@href").get()
        if (response.meta["id"] == self.total_chap) or (
            response.meta["id"] == self.stop_chap
        ):
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
    r.add_xpath("title", '//*[@class="booknav2"]/h1//text()')
    r.add_xpath("author", '//*[@class="booknav2"]/p/a/text()')
    r.add_value("types", "--")
    r.add_xpath("foreword", '//*[@class="navtxt"]/p[1]/text()')
    r.add_xpath("image_urls", '//*[@class="bookimg2"]/img/@src')
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
    r.add_xpath("title", "//div[3]//h1/text()")
    content = response.xpath('//div[@class="txtnav"]/text()').getall()
    content[3] = ''
    r.add_value("content", content)
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
