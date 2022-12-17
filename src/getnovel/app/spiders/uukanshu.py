"""Get novel from domain uukanshu.

.. _Web site:
   https://www.uukanshu.com

"""
from pathlib import Path

import scrapy


class UukanshuSpider(scrapy.Spider):
    """Define spider for domain: uukanshu"""

    name = "uukanshu"

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
        self.menu = list()
        self.domain = "https://www.uukanshu.com"

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
        # download cover
        yield scrapy.Request(
            url="https:{0}".format(
                response.xpath('//*[@class="jieshao-img"]/a/img/@src').get()
            ),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)
        self.menu: list = response.xpath('//*[@id="chapterList"]/li/a/@href').getall()
        self.menu.reverse()
        if self.start_chap > len(self.menu):
            raise scrapy.exceptions.CloseSpider(
                reason="Start chapter index is greater than menu list"
            )
        yield scrapy.Request(
            url=self.domain + self.menu[self.start_chap - 1],  # goto start chapter
            meta={"id": self.start_chap},
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
        if (response.meta["id"] == len(self.menu)) or (
            response.meta["id"] == self.stop_chap
        ):
            raise scrapy.exceptions.CloseSpider(reason="Done")
        link_next_chap = self.domain + self.menu[response.meta["id"]]
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url=link_next_chap,
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
    title: str = (
        response.xpath('//*[@class="jieshao_content"]/h1/a/@title')
        .get()
        .replace("最新章节", "")
    )
    author = response.xpath('//*[@class="jieshao_content"]/h2/a/text()').get()
    types = ["--"]
    foreword = response.xpath('//*[@class="jieshao_content"]/h3/text()').getall()
    info = list()
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
    # get chapter
    chapter = response.xpath('//*[@id="timu"]/text()').get()
    # get content
    content: list = response.xpath(
        '//*[@id="contentbox"]//text()[not(parent::script)]'
    ).getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
