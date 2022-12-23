"""Get novel on domain metruyencv.

.. _Web sites:
   https://metruyencv.com

"""

from pathlib import Path

from scrapy import Spider
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class MeTruyenCVSpider(Spider):
    """Define spider for domain: metruyencv"""

    name = "metruyencv"

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
        self.save_path = save_path
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.total = 0

    def parse(self, response: Response):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to the start chapter.
        """
        self.total = int(response.xpath('//a[@id="nav-tab-chap"]/span[2]/text()').get())
        if self.start_chap > self.total:
            self.logger.error(msg="Start chapter is greater than total chapters")
            raise CloseSpider(reason="Stopped")
        yield get_info(response)
        yield response.follow(
            url=f"{response.url}/chuong-{self.start_chap}/",
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
        next_url = (
            f'{response.url.rsplit("/", 2)[0]}/chuong-{str(response.meta["id"] + 1)}/'
        )
        if (response.meta["id"] == self.stop_chap) or (
            response.meta["id"] >= self.total
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
    r.add_xpath("title", '//h1[@class="h3 mr-2"]/a/text()')
    r.add_xpath("author", '//ul[@class="list-unstyled mb-4"]/li[1]/a/text()')
    r.add_xpath("types", '//ul[@class="list-unstyled mb-4"]/li[position()>1]/a/text()')
    r.add_xpath("foreword", '//div[@class="content"]/p/text()')
    r.add_xpath("image_urls", '//div[@class="media"]//img[1]/@src')
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
    r.add_xpath("title", '//div[contains(@class,"nh-read__title")]/text()')
    r.add_xpath("content", '//div[@id="article"]/text()')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
