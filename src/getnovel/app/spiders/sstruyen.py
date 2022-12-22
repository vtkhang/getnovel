"""Get novel from domain sstruyen.

.. _Web site:
   https://sstruyen.vn/

"""

from pathlib import Path

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class SSTruyenSpider(Spider):
    """Declare spider for domain: sstruyen"""

    name = "sstruyen"

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
        """Extract info and send request to start chapter.

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
            url=response.urljoin(f"chuong-{str(self.start_chap)}/"),
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
        Request
            Chapter item.
        Request
            Request to the next chapter.
        """
        yield get_content(response)
        npu = response.xpath(
            '//*[@id="j_content"]/div[3]//li[@class="next"]/a/@href'
        ).get()
        if (npu is None) or (response.meta["id"] == self.stop_chap):
            raise CloseSpider(reason="Done")
        yield Request(
            url=response.urljoin(npu),
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response):
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", "//div[5]//h1//text()")
    r.add_xpath("author", '//*[@itemprop="author"]/text()')
    r.add_xpath("types", "//div[5]//div[2]/div[3]//p[2]/a/text()")
    r.add_xpath("foreword", "//div[5]//div[3]/p/text()")
    r.add_xpath("image_urls", "//div[5]//div[1]/img/@src")
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
    r.add_xpath("title", '//*[@id="j_content"]//h2//text()')
    r.add_xpath("content", '//*[@id="j_content"]//p/text()')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
