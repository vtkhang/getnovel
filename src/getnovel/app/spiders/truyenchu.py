"""Get novel on domain truyenchu.

.. _Web site:
   https://truyenchu.vn/

"""

from scrapy import Spider, Selector
from scrapy.http import Response, FormRequest
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenChuSpider(Spider):
    """Define spider for domain: truyenchu"""

    name = "truyenchu"

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
        total_chap = 50
        start_chap = self.sa - 1
        menu_page_have_start_chap = start_chap // total_chap + 1
        pos_of_start_chap_in_menu = start_chap % total_chap
        yield FormRequest(
            method="GET",
            url="https://truyenchu.vn/api/services/list-chapter",
            meta={"pos_start": pos_of_start_chap_in_menu},
            callback=self.parse_toc,
            formdata={
                "type": "list_chapter",
                "tid": res.xpath('//input[@id="truyen-id"]/@value').get(),
                "tascii": res.xpath('//input[@id="truyen-ascii"]/@value').get(),
                "page": str(menu_page_have_start_chap),
            },
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
        mini_toc = (
            Selector(text=res.json()["chap_list"]).xpath("//li//a/@href").getall()
        )
        yield res.follow(
            url=mini_toc[res.meta["pos_start"]],
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
        neu = res.xpath('//a[@id="next_chap"]/@href').get()
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
    imgurl = res.xpath('//div[@class="book"]/img/@src').get()
    r = InfoLoader(item=Info(), response=res)
    r.add_xpath("title", '//h1[@class="story-title"]/a/text()')
    r.add_xpath("author", '//*[@itemprop="author"]//span/text()')
    r.add_xpath("types", '//*[@id="truyen"]//div[1]//div[1]/div[3]/a/text()')
    r.add_xpath("foreword", '//*[@id="truyen"]/div[1]/div[2]/div[2]/div[2]//text()')
    r.add_value("image_urls", res.urljoin(imgurl))
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
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath("content", '//div[@id="chapter-c"]//text()[not(parent::script)]')
    return r.load_item()
