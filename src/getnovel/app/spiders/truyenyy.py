"""Get novel on domain truyenyy.

.. _Web site:
   https://truyenyy.vip/

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from getnovel.app.itemloaders import InfoLoader, ChapterLoader
from getnovel.app.items import Info, Chapter


class TruyenYYSpider(Spider):
    """Define spider for domain: truyenyy"""

    name = "truyenyy"

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
        total_chap = 40
        start_chap = self.sa - 1
        menu_page_have_start_chap = start_chap // total_chap + 1
        pos_of_start_chap_in_menu = start_chap % total_chap
        yield res.follow(
            url=f"danh-sach-chuong/?p={menu_page_have_start_chap}",
            meta={"pos_start": pos_of_start_chap_in_menu},
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
        yield res.follow(
            url=res.xpath(
                f'(//div[2]//tbody//td/a/@href)[{res.meta["pos_start"] + 1}]'
            ).get(),
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
        if res.xpath("//div[2]/div[2]/div[4]//div[2]").get():
            raise CloseSpider(reason="Reached vip chapters!")
        yield get_content(res)
        neu = res.xpath("//div[2]/div[2]/a/@href").get()
        if (neu is None) or (res.meta["id"] == self.so):
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
    r.add_value("id", str(res.meta["id"]))
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
