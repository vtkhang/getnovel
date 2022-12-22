"""Get novel from domain webtruyen.

.. _Web site:
   https://truyenchu.vn/

"""

import json
from pathlib import Path

from scrapy import Spider, Request, FormRequest, Selector
from scrapy.http import Response
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenChuSpider(Spider):
    """Declare spider for domain: truyenchu"""

    name = "truyenchu"

    def __init__(
        self,
        url: str,
        start_chap: int,
        stop_chap: int,
        save_path: Path,
        *args,
        **kwargs
    ):
        """Initialize attributes.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        save_path : Path
            Path of raw directory.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling from this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.save_path = save_path
        self.mini_toc = []

    def parse(self, response: Response):
        """Extract info and send request to table of content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Info item.
        Request
            Request to the start chapter.
        """
        yield get_info(response)
        # calculate the position of start_chap in menu list
        total_chap = 50
        start_chap = self.start_chap - 1
        menu_page_have_start_chap = start_chap // total_chap + 1
        pos_of_start_chap_in_menu = start_chap % total_chap
        fd = {
            "type": "list_chapter",
            "tid": response.xpath('//input[@id="truyen-id"]/@value').get(),
            "tascii": response.xpath('//input[@id="truyen-ascii"]/@value').get(),
            "page": str(menu_page_have_start_chap),
        }
        yield FormRequest(
            method="GET",
            url="https://truyenchu.vn/api/services/list-chapter",
            formdata=fd,
            meta={"pos_start": pos_of_start_chap_in_menu},
            callback=self.parse_start,
        )

    def parse_start(self, response: Response):
        """Send request to the start chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter.
        """
        t = json.loads(response.text)
        if "chap_list" not in t:
            raise CloseSpider(reason="response of xhr doesn't have chap_list")
        if t["chap_list"] == "":
            raise CloseSpider(reason="start chapter is not exists")
        mini_toc = Selector(text=t["chap_list"]).xpath("//li//a/@href").getall()
        yield Request(
            url=response.urljoin(mini_toc[response.meta["pos_start"]]),
            callback=self.parse_content,
            meta={"id": self.start_chap},
        )

    def parse_content(self, response: Response):
        """Extract content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Chapter item.
        Request
            Request to the next chapter.
        """
        yield get_content(response)
        next_url = response.xpath('//a[@id="next_chap"]/@href').get()
        if (next_url == "#") or (response.meta["id"] == self.stop_chap):
            raise CloseSpider(reason="Done")
        yield Request(
            url=response.urljoin(next_url),
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response):
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    imgurl = response.xpath('//div[@class="book"]/img/@src').get()
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//h1[@class="story-title"]/a/text()')
    r.add_xpath("author", '//*[@itemprop="author"]//span/text()')
    r.add_xpath("types", '//*[@id="truyen"]//div[1]//div[1]/div[3]/a/text()')
    r.add_xpath("foreword", '//*[@id="truyen"]/div[1]/div[2]/div[2]/div[2]//text()')
    r.add_value("image_urls", response.urljoin(imgurl))
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response):
    """Get chapter content.

    Parameters
    ----------
    response : Response
        The response to parse.
    """
    r = ChapterLoader(item=Chapter(), response=response)
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath("content", '//div[@id="chapter-c"]//text()[not(parent::script)]')
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
