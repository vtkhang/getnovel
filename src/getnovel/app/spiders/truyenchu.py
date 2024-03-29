"""Get novel on domain truyenchu.

.. _Website:
   https://truyenchu.vn/

"""

from scrapy import Selector, Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest, Response

from getnovel.app.itemloaders import ChapterLoader, InfoLoader
from getnovel.app.items import Chapter, Info


class TruyenChuSpider(Spider):
    """Define spider for domain: truyenchu.

    Attributes
    ----------
    name : str
        Name of the spider.
    title_pos : int
        Position of the title in the novel url.
    lang : str
        Language code of novel.
    """

    name = "truyenchu"
    title_pos = -1
    lang_code = "vi"

    def __init__(self: "TruyenChuSpider", url: str, start: int, stop: int) -> None:
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
        self.c = "vi"  # language code

    def parse(self: "TruyenChuSpider", res: Response) -> None:
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

    def parse_toc(self: "TruyenChuSpider", res: Response) -> None:
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
            meta={"index": self.sa},
            callback=self.parse_content,
        )

    def parse_content(self: "TruyenChuSpider", res: Response) -> None:
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
        if (neu == "#") or (res.meta["index"] == self.so):
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
    r.add_value("index", str(res.meta["index"]))
    r.add_value("url", res.url)
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath("content", '//div[@id="chapter-c"]//text()[not(parent::script)]')
    return r.load_item()
