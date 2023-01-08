"""Get novel on domain 69shu.

   Note: Can't get all chapters if using start chapter,
   use -1 to get all chapters instead.

.. _Web site:
   https://www.69shu.com

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class SixNineShuSpider(Spider):
    """Define spider for domain: 69shu"""

    name = "69shu"

    def __init__(self, u: str, start: int, stop: int, *args, **kwargs):
        """Initialize attributes.

        Parameters
        ----------
        u : str
            Url of the novel information page.
        start: int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u]
        self.sa = int(start)
        self.so = int(stop)
        self.c = "zh"  # language code

    def parse(self, res: Response, *args, **kwargs):
        """Extract info and send request to the table of content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to the table of content.
        """
        yield get_info(res)
        yield res.follow(
            url=res.xpath("//div[3]//div[3]/a/@href").get(),
            callback=self.parse_toc,
        )

    def parse_toc(self, res: Response):
        """Extract link of the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter.
        """
        su = res.xpath(
            f'(//*[@id="catalog"]//a/@href)[{self.sa}]'
        ).get()
        if su is None:
            self.logger.error(msg="Start chapter is greater than total chapter")
            raise CloseSpider(reason="cancelled")
        yield res.follow(
            url=res.xpath(f'(//*[@id="catalog"]//a/@href)[{self.sa}]').get(),
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self, res: Response):
        """Extract content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Chapter
            Chapter item.

        Request
            Request to the next chapter.
        """
        yield get_content(res)
        neu = res.xpath("//div[3]//a[4]/@href").get()
        if ("htm" in neu) or (res.meta["id"] == self.so):
            raise CloseSpider(reason="done")
        yield res.follow(
            url=neu,
            meta={"id": res.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(res: Response) -> Info:
    """Get novel information.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=res)
    r.add_xpath("title", '//*[@class="booknav2"]/h1//text()')
    r.add_xpath("author", '//*[@class="booknav2"]/p/a/text()')
    r.add_value("types", "--")
    r.add_xpath("foreword", '//*[@class="navtxt"]/p[1]/text()')
    r.add_xpath("image_urls", '//*[@class="bookimg2"]/img/@src')
    r.add_value("url", res.request.url)
    return r.load_item()


def get_content(res: Response) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=res)
    r.add_value("id", str(res.meta["id"]))
    r.add_value("url", res.url)
    r.add_xpath("title", "//div[3]//h1/text()")
    r.add_xpath("content", '//div[@class="txtnav"]/text()')
    return r.load_item()
