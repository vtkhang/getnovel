# -*- coding: utf-8 -*-
"""Get novels from domain 69shu.

.. _Web site:
   https://www.69shu.com

"""
from pathlib import Path

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.exceptions import CloseSpider


class SixNineshuSpider(Spider):
    """Define spider for domain: 69shu."""

    name = "69shu"

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
        self.sp = save_path
        self.sa = start_chap
        self.so = stop_chap
        self.toc: list = []

    def parse(self, response: Response, **kwargs):
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
        c_url = response.xpath('//*[@class="bookimg2"]/img/@src').get()
        yield Request(
            url=c_url,
            callback=self.parse_cover,
        )
        get_info(response, self.sp)
        toc_str = response.xpath('//*[@class="btn more-btn"]/@href').get()
        toc_url = f"https://www.69shu.com{toc_str}"
        yield Request(url=toc_url, callback=self.parse_toc)

    def parse_toc(self, response: Response) -> None:
        """Extract info of the novel and get the link of the
        table of content (toc).

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter.
        """
        self.toc: list = response.xpath('//*[@id="catalog"]/ul/li/a/@href').getall()
        if self.sa > len(self.toc):
            raise CloseSpider(
                reason="Start chapter index is greater than total chapters."
            )
        yield Request(
            url=self.toc[self.sa - 1],  # goto start chapter
            meta={"id": self.sa},
            callback=self.parse_content,
        )

    def parse_cover(self, response: Response):
        """Download the cover of novel.

        Parameters
        ----------
        response : Response
            The response to parse.
        """
        (self.sp / "cover.jpg").write_bytes(response.body)

    def parse_content(self, response: Response):
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
        get_content(response, self.sp)
        if (response.meta["id"] == len(self.toc)) or (response.meta["id"] == self.so):
            raise CloseSpider(reason="Done")
        link_next_chap = self.toc[response.meta["id"]]
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield Request(
            url=link_next_chap,
            headers=response.request.headers,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: Response, save_path: Path) -> None:
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # extract info
    title: str = response.xpath('//*[@class="booknav2"]/h1/a/text()').get()
    t = response.xpath('//*[@class="booknav2"]/p/a/text()').getall()
    author: str = t[0]
    types = ["--"]
    if len(t) == 2:
        types = t[1]
    foreword = response.xpath('//*[@class="navtxt"]/p[1]/text()').getall()
    info = []
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(", ".join(types))
    info.extend(foreword)
    # write info to file
    (save_path / "foreword.txt").write_text("\n".join(info), encoding="utf-8")


def get_content(response: Response, save_path: Path) -> None:
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    content: list = response.xpath(
        '//*[@class="txtnav"]//text()[not(parent::h1) '
        "and not(parent::span) and not(parent::script)]"
    ).getall()
    # content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
