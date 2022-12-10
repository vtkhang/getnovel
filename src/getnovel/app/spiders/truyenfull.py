"""Get novel from domain truyenfull.

.. _Web site:
   https://truyenfull.vn

"""
from pathlib import Path

import scrapy


class TruyenFullSpider(scrapy.Spider):
    """Define spider for domain: truyenfull."""

    name = "truyenfull"

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
            url=response.xpath(
                '//div[@class="book"]/img[@itemprop="image"]/@src'
            ).get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)
        yield scrapy.Request(
            url=f"{response.url}chuong-{self.start_chap}/",  # goto start chapter
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
        link_next_chap = response.xpath('//a[@id="next_chap"]/@href').getall()[0]
        if ("javascript:void(0)" in link_next_chap) or response.meta[
            "id"
        ] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
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
    title = response.xpath('//*[@id="truyen"]/div[1]/div[1]/h3/text()').get()
    author = response.xpath(
        '//*[@id="truyen"]/div[1]/div[1]/div[2]/div[2]/div[1]/a/text()'
    ).get()
    types = response.xpath(
        '//*[@id="truyen"]/div[1]/div[1]/div[2]/div[2]/div[2]/a/text()'
    ).getall()
    foreword = response.xpath(
        '//*[@id="truyen"]/div[1]/div[1]/div[3]/div[2]//text()'
    ).getall()
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
    # get chapter
    chapter = (
        "Chương " + response.xpath('/html//a[@class="chapter-title"]/text()').get()
    )
    # get content
    content = response.xpath(
        '/html//div[@id="chapter-c"]//text()[parent::div or parent::i]'
    ).getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
