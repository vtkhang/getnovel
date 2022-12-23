"""Get novel on domain uukanshu.

.. _Web site:
   https://www.uukanshu.com

"""

from scrapy import Spider
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class UukanshuSpider(Spider):
    """Define spider for domain: uukanshu"""

    name = "uukanshu"

    def __init__(
        self,
        url: str,
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
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling at this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.toc = []
        self.toc_len = 0

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
        yield get_info(response)
        self.toc.extend(response.xpath('//*[@id="chapterList"]/li/a/@href').getall())
        self.toc_len = len(self.toc)
        if self.start_chap > self.toc_len:
            raise CloseSpider(reason="Start chapter index is greater than menu list")
        yield response.follow(
            url=self.toc[self.toc_len - self.start_chap],
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
        if (response.meta["id"] == self.toc_len) or (
            response.meta["id"] == self.stop_chap
        ):
            raise CloseSpider(reason="Done")
        yield response.follow(
            url=self.toc[self.toc_len - response.meta["id"] - 1],
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response):
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
    title = (
        response.xpath('//*[@class="jieshao_content"]/h1/a/@title')
        .get()
        .replace("最新章节", "")
    )
    imghref = response.xpath('//*[@class="jieshao-img"]/a/img/@src').get()
    r = InfoLoader(item=Info(), response=response)
    r.add_value("title", title)
    r.add_xpath("author", '//*[@class="jieshao_content"]/h2/a/text()')
    r.add_value("types", "--")
    r.add_xpath("foreword", '//*[@class="jieshao_content"]/h3/text()')
    r.add_value("image_urls", response.urljoin(imghref))
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response):
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
    r.add_xpath("title", '//*[@id="timu"]/text()')
    r.add_xpath("content", '//*[@id="contentbox"]//text()[not(parent::script)]')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
