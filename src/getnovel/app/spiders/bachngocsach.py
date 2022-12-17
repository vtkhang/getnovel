"""Get novel from domain bachngocsach.

.. _Web site:
   https://bachngocsach.com/reader

"""
from pathlib import Path

import scrapy


class BachNgocSachSpider(scrapy.Spider):
    """Define spider for domain: bachngocsach"""

    name = "bachngocsach"

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
        self.stop_chap = int(stop_chap)

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
        # request cover
        yield scrapy.Request(
            response.xpath('//div[@id="anhbia"]/img/@src').get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)  # get info and write it to save path
        yield scrapy.Request(
            url=response.url + r"/muc-luc?page=all", callback=self.parse_start_chapter
        )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Parameters
        ----------
        response : Response
            The response to parse.
        """
        (self.save_path / "cover.jpg").write_bytes(response.body)

    def parse_start_chapter(self, response: scrapy.http.Response):
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
        yield scrapy.Request(
            url="https://bachngocsach.com"
            + response.xpath('//*[@class="chuong-link"]/@href').getall()[
                self.start_chap - 1
            ],
            meta={"id": self.start_chap},  # id of the start chapter
            callback=self.parse_content,
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
        t = response.xpath('//a[contains(@class,"page-next")]/@href').getall()
        if (len(t) <= 0) or response.meta["id"] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url="https://bachngocsach.com" + t[0],
            headers=response.request.headers,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: scrapy.http.Response, save_path: Path):
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # extract info
    title = response.xpath('//*[@id="truyen-title"]/text()').get()
    author = response.xpath('//div[@id="tacgia"]/a/text()').get()
    types = response.xpath('//div[@id="theloai"]/a/text()').getall()
    foreword = response.xpath('//div[@id="gioithieu"]/div/p/text()').getall()
    info = []
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(", ".join(types))
    info.extend(foreword)
    # write info to file
    (save_path / "foreword.txt").write_text("\n".join(info), encoding="utf-8")


def get_content(response: scrapy.http.Response, save_path: Path):
    """Get content of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # extract chapter title
    chapter = response.xpath('//h1[@id="chuong-title"]/text()').get()
    # extract content
    content = response.xpath('//div[@id="noi-dung"]/p/text()').getall()
    content.insert(0, chapter)
    # write content to file
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
