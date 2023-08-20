"""Get novel on domain metruyencv.

.. _Web site:
   https://metruyencv.com

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class MeTruyenCVSpider(Spider):
    """Define spider for domain: metruyencv.

    Attributes:
    ----------
    name : str
        Name of the spider.
    start_urls : list
        List of url to start crawling from.
    sa : int
        The chapter index to start crawling.
    so : int
        The chapter index to stop crawling after that.
    c : str
        Language code of novel.
    """

    name = "metruyencv"

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
        self.c = "vi"  # language code
        self.n = 0  # total chapters

    def parse(self, res: Response):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields:
        ------
        Info
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(res)
        self.n = int(res.xpath('//a[@id="nav-tab-chap"]/span[2]/text()').get())
        yield Request(
            url=f"{res.url}/chuong-{self.sa}/",
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self, res: Response):
        """Extract content.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields:
        ------
        Chapter
            Chapter item.

        Request
            Request to the next chapter.
        """
        yield get_content(res)
        if (res.meta["id"] >= self.n) or (res.meta["id"] == self.so):
            raise CloseSpider(reason="done")
        neu = f'{res.url.rsplit("/", 2)[0]}/chuong-{str(res.meta["id"] + 1)}/'
        yield Request(
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

    Returns:
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=res)
    r.add_xpath("title", '//h1[@class="h3 mr-2"]/a/text()')
    r.add_xpath("author", '//ul[@class="list-unstyled mb-4"]/li[1]/a/text()')
    r.add_xpath("types", '//ul[@class="list-unstyled mb-4"]/li[position()>1]/a/text()')
    r.add_xpath("foreword", '//div[@class="content"]/p/text()')
    r.add_xpath("image_urls", '//div[@class="media"]//img[1]/@src')
    r.add_value("url", res.request.url)
    return r.load_item()


def get_content(res: Response) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    res : Response
        The response to parse.

    Returns:
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=res)
    r.add_value("id", str(res.meta["id"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//div[contains(@class,"nh-read__title")]/text()')
    r.add_xpath("content", '//div[@id="article"]/text()')
    return r.load_item()
