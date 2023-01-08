"""Get novel on domain uukanshu.

.. _Web site:
   https://www.uukanshu.com

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class UukanshuSpider(Spider):
    """Define spider for domain: uukanshu"""

    name = "uukanshu"

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
        self.t = []  # table of content
        self.n = 0  # total chapters

    def parse(self, res: Response, *args, **kwargs):
        """Extract info and send request to the start chapter.

        Parameters
        ----------
        res : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(res)
        self.t.extend(res.xpath('//*[@id="chapterList"]/li/a/@href').getall())
        self.t.reverse()
        self.n = len(self.t)
        yield res.follow(
            url=self.t[self.sa - 1],
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
        if (res.meta["id"] >= self.n) or (res.meta["id"] == self.so):
            raise CloseSpider(reason="done")
        yield res.follow(
            url=self.t[res.meta["id"]],
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
    title = (
        res.xpath('//*[@class="jieshao_content"]/h1/a/@title').get().replace("最新章节", "")
    )
    imghref = res.xpath('//*[@class="jieshao-img"]/a/img/@src').get()
    r = InfoLoader(item=Info(), response=res)
    r.add_value("title", title)
    r.add_xpath("author", '//*[@class="jieshao_content"]/h2/a/text()')
    r.add_value("types", "--")
    r.add_xpath("foreword", '//*[@class="jieshao_content"]/h3/text()')
    r.add_value("image_urls", res.urljoin(imghref))
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
    r.add_xpath("title", '//*[@id="timu"]/text()')
    r.add_xpath("content", '//*[@id="contentbox"]//text()[not(parent::script)]')
    return r.load_item()
