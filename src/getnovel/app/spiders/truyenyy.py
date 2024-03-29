"""Get novel on domain truyenyy.

.. _Website:
   https://truyenyy.vip/

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class TruyenYYSpider(Spider):
    """Define spider for domain: truyenyy.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "truyenyy"
    title_pos = -2
    lang_code = "vi"

    def __init__(self: "TruyenYYSpider", url: str, start: int, stop: int) -> None:
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

    def parse(self: "TruyenYYSpider", res: Response) -> None:
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
        total_chap = 40
        start_chap = self.sa - 1
        menu_page_have_start_chap = start_chap // total_chap + 1
        pos_of_start_chap_in_menu = start_chap % total_chap
        yield res.follow(
            url=f"danh-sach-chuong/?p={menu_page_have_start_chap}",
            meta={"pos_start": pos_of_start_chap_in_menu},
            callback=self.parse_toc,
        )

    def parse_toc(self: "TruyenYYSpider", res: Response) -> None:
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
        yield res.follow(
            url=res.xpath(
                f'(//div[2]//tbody//td/a/@href)[{res.meta["pos_start"] + 1}]',
            ).get(),
            meta={"index": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self: "TruyenYYSpider", res: Response) -> None:
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
        if res.xpath("//div[2]/div[2]/div[4]//div[2]").get():
            raise CloseSpider(reason="Reached vip chapters!")
        yield get_content(res)
        neu = res.xpath("//div[2]/div[2]/a/@href").get()
        if (neu is None) or (res.meta["index"] == self.so):
            raise CloseSpider(reason="done")
        yield res.follow(
            url=neu,
            meta={"index": res.meta["index"] + 1},
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
    r.add_xpath("title", '//h1[@class="name"]/text()')
    r.add_xpath("author", '//div[@class="info"]/div[1]/a/text()')
    r.add_xpath("types", '//div[@class="info"]/ul[1]/li[1]//text()')
    r.add_xpath("foreword", '//*[@id="id_novel_summary"]//text()')
    r.add_xpath("image_urls", '//div[@class="novel-info"]/a/img/@data-src')
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
    r.add_value("index", str(res.meta["index"]))
    r.add_value("url", res.url)
    r.add_xpath(
        "title",
        "//div[2]//h1/span/text() | //div[2]//h2/text()",
    )
    r.add_xpath(
        "content",
        '//*[@id="inner_chap_content_1"]/p/text()',
    )
    return r.load_item()
