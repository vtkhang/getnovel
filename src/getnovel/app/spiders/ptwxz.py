"""Get novel from domain ptwxz.

.. _Web site:
   https://www.ptwxz.com

"""

from pathlib import Path

from scrapy import Spider
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
            url=response.xpath('//*[@id="content"]//a[1]/@href').get(),
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
        try:
            yield response.follow(
                url=response.xpath(
                    f'(//div[@class="centent"]//a)[{self.start_chap}]'
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
        next_url = response.xpath("//div[3]/a[3]").attrib["href"]
        if ("i" in next_url) or (response.meta["id"] == self.stop_chap):
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
    ihref = response.xpath('//*[@id="content"]//td[2]//img').attrib["src"]
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//*[@id="content"]//tr[1]//h1/text()')
    r.add_xpath("author", '//*[@id="content"]//tr[2]/td[2]/text()')
    r.add_xpath("types", '//*[@id="content"]//tr[2]/td[1]/text()')
    r.add_xpath("foreword", '//*[@id="content"]//td[2]//text()[4]')
    r.add_value("image_urls", response.urljoin(ihref))
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
    r.add_xpath("title", "//h1/text()")
    r.add_xpath("content", "//body/text()")
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
