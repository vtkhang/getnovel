"""Get novel on domain dtruyen.

.. _Web site:
   https://dtruyen.com/

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class DTruyenSpider(Spider):
    """Define spider for domain: dtruyen"""

    name = "dtruyen"

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
                f'(//*[@id="chapters"]/ul//a/@href)[{res.meta["pos_start"]}]'
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
