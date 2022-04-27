"""Get novel from domain webtruyen.

.. _Web site:
   https://truyenchu.vn/

"""
import json
from pathlib import Path

import scrapy


class TruyenchuSpider(scrapy.Spider):
    """Define spider for domain: truyenchu."""

    name = "truyenchu"

    def __init__(
        self,
        url: str,
        save_path: Path,
        start_chap: int,
        stop_chap: int,
        *args,
        **kwargs,
    ):
        """Initialize the attributes for this spider.

        Parameters
        ----------
        url : str
            The link of the novel information page.
        save_path : Path
            Path of raw directory.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling from this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.save_path = save_path
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.info_url = str()
        self.menu = []

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the
        table of content (toc).

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the cover image page and toc page.
        """
        self.info_url = response.request.url
        # get cover
        cover_link = "https://truyenchu.vn{}".format(
            response.xpath('//div[@class="book"]/img/@src').get()
        )
        yield scrapy.Request(url=cover_link, callback=self.parse_cover)
        get_info(response, self.save_path)
        # request menu list
        total_chap = 50
        # calculate the position of start_chap in menu list
        menu_page_have_start_chap = self.start_chap // total_chap + 1
        pos_of_start_chap_in_menu = self.start_chap % total_chap
        if pos_of_start_chap_in_menu == -1:
            menu_page_have_start_chap -= 1
            pos_of_start_chap_in_menu = total_chap
        pos_of_start_chap_in_menu -= 1  # because list in python have index begin with 0
        fd = {
            "type": "list_chapter",
            "tid": response.xpath('//input[@id="truyen-id"]/@value').get(),
            "tascii": response.xpath('//input[@id="truyen-ascii"]/@value').get(),
            "page": str(menu_page_have_start_chap),
        }
        yield scrapy.FormRequest(
            method="GET",
            url="https://truyenchu.vn/api/services/list-chapter",
            headers=response.request.headers,
            formdata=fd,
            meta={"pos_start": pos_of_start_chap_in_menu},
            callback=self.parse_start,
        )

    def parse_start(self, response: scrapy.http.Response):
        """Extract link of the start chapter.

        Parameters
        ----------
        response : scrapy.http.Response
            The response to parse.

        Yields
        ------
        scrapy.Request
            Request to the start chapter.
        """
        t = json.loads(response.body.decode("utf8").replace("'", '"'))
        if "chap_list" not in t:
            raise scrapy.exceptions.CloseSpider(
                reason="response of xhr doesn't have chap_list."
            )
        if t["chap_list"] == "":
            raise scrapy.exceptions.CloseSpider(reason="start chapter is not exists.")
        s: scrapy.Selector = scrapy.Selector(text=t["chap_list"])
        chapter_links = s.xpath("//li//a/@href").getall()
        self.menu.extend(chapter_links)
        yield scrapy.Request(
            url="https://truyenchu.vn{}".format(
                chapter_links[response.meta["pos_start"]]
            ),
            callback=self.parse_content,
            meta={"id": self.start_chap},
        )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the next chapter.
        """
        get_content(response, self.save_path)
        npu = response.xpath('//a[@id="next_chap"]/@href').get()
        if npu.replace("/", "") == self.info_url.rsplit("/", 1)[1]:
            i1 = str(response.meta["id"] + 1)
            i2 = str((response.meta["id"] + 1) // 50 + 1)
            raise scrapy.exceptions.CloseSpider(
                reason="The chapter " + i1 + " at " + i2 + " have errors."
            )
        if (npu == "#") or response.meta["id"] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url="https://truyenchu.vn{}".format(npu),
            headers=response.request.headers,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Parameters
        ----------
        response : Response
            The response to parse.
        """
        (self.save_path / "cover.jpg").write_bytes(response.body)


def get_info(response: scrapy.http.Response, save_path: Path):
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # get title
    title = response.xpath('//h1[@class="story-title"]/a/text()').get()
    # get book info
    author = response.xpath('//div[@itemprop="author"]/a/span/text()').get()
    types = response.xpath(
        '//div[@class="info"]/div/a[@itemprop="genre"]/text()'
    ).getall()
    foreword = response.xpath('//div[@class="desc-text"]/p/text()').get()
    info = list()
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(", ".join(types))
    info.extend(foreword.split("\n"))
    (save_path / "foreword.txt").write_text(
        "\n".join([x.replace("\n", " ") for x in info]), encoding="utf-8"
    )


def get_content(response: scrapy.http.Response, save_path: Path):
    """Get content of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    chapter = response.xpath('//a[@class="chapter-title"]/@title').get()
    # get content
    content = response.xpath(
        '//div[@id="chapter-c"]//text()[not(parent::script)]'
    ).getall()
    if chapter is None or content is None:
        chapter = "Chương này bị lỗi. Mời lên website của truyện để tìm hiểu thêm."
        content = []
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
