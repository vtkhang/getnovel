"""Get novel on domain 69shuba.

   Note: Can't get all chapters if using start chapter,
   use -1 to get all chapters instead.

.. _Website:
   https://www.69shuba.com

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class SixNineShubaSpider(Spider):
    """Define spider for domain: 69shuba.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "69shuba"
    title_pos = -1
    lang_code = "zh"

    def __init__(self: "SixNineShubaSpider", url: str, start: int, stop: int) -> None:
        """Initialize attributes.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        start: int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        """
        self.start_urls = [url]
        self.sa = int(start)
        self.so = int(stop)

    def parse(self: "SixNineShubaSpider", res: Response) -> None:
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
            url=res.xpath(
                "/html/body/div[2]/ul/li[1]/div[1]/div/div[3]/a[1]/@href",
            ).get(),
            callback=self.parse_toc,
        )

    def parse_toc(self: "SixNineShubaSpider", res: Response) -> None:
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
        su = res.xpath(f'(//*[@id="catalog"]//a/@href)[{self.sa}]').get()
        if su is None:
            self.logger.error(msg="Start chapter is greater than total chapter")
            raise CloseSpider(reason="cancelled")
        yield res.follow(
            url=su,
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self: "SixNineShubaSpider", res: Response) -> None:
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
        neu = res.xpath("/html/body/div[2]/div[1]/div[4]/a[4]/@href").get()
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
