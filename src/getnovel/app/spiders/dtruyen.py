"""Get novel on domain dtruyen.

.. _Website:
   https://dtruyen.com/

"""

from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class DTruyenSpider(Spider):
    """Define spider for domain: dtruyen.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "dtruyen"
    title_pos = -2
    lang_code = "vi"

    def __init__(self: "DTruyenSpider", url: str, start: int, stop: int) -> None:
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

    def parse(self: "DTruyenSpider", res: Response) -> None:
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
        total_chap = 30
        sa = self.sa - 1
        menu_page_have_start_chap = sa // total_chap + 1
        pos_of_start_chap_in_menu = sa % total_chap + 1
        yield Request(
            url=f"{res.url}{menu_page_have_start_chap}/",
            meta={
                "pos_start": pos_of_start_chap_in_menu,
            },
            callback=self.parse_toc,
        )

    def parse_toc(self: "DTruyenSpider", res: Response) -> None:
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
                f'(//*[@id="chapters"]/ul//a/@href)[{res.meta["pos_start"]}]',
            ).get(),
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self: "DTruyenSpider", res: Response) -> None:
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
        if res.xpath('//*[@id="pre-vip"]/text()').get():
            raise CloseSpider(reason="Reached VIP Chapters!")
        yield get_content(res)
        neu = res.xpath('//*[@id="chapter"]/div[1]/a[4]/@href').get()
        if (neu == "#") or (res.meta["id"] == self.so):
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
    r.add_xpath("title", '//h1[@itemprop="name"]/text()')
    r.add_xpath("author", '//a[@itemprop="author"]/text()')
    r.add_xpath("types", '//a[@itemprop="genre"]/text()')
    r.add_xpath("foreword", '//*[@id="story-detail"]/div[2]/div[3]//text()')
    r.add_xpath("image_urls", '//*[@id="story-detail"]/div[1]/div[1]/img/@src')
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
    r.add_xpath("title", '//*[@id="chapter"]/header/h2/text()')
    r.add_xpath("content", '//*[@id="chapter-content"]/text()')
    return r.load_item()
