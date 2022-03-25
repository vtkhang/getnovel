"""Get novel from domain sstruyen.

.. _Web site:
   https://sstruyen.com/

"""
from pathlib import Path

import scrapy


class SSTruyenSpider(scrapy.Spider):
    """Define spider for domain: sstruyen."""

    name = "sstruyen"

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
        self.base_url = "https://sstruyen.com"

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
        # get cover
        cover_link = response.xpath(
            "//*[@class='sstbcover']/@data-pagespeed-high-res-src"
        ).get()
        yield scrapy.Request(url=cover_link, callback=self.parse_cover)
        get_info(response, self.save_path)
        yield scrapy.Request(
            url=response.url + "chuong-" + str(self.start_chap) + "/",
            callback=self.parse_content,
            meta={"id": self.start_chap},
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
        npu = response.xpath('//*[@id="j_content"]//li[@class="next"]/a/@href').get()
        if (npu is None) or response.meta["id"] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url=self.base_url + npu,
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
    # get title
    title = response.xpath('//*[@class="title"]/h1/a/text()').get()
    # get book info
    author = response.xpath('//*[@itemprop="author"]/text()').get()
    types = response.xpath(
        "/html/body/div[5]/div/div/div[1]/div[1]/div[2]/div[3]/div/p[2]/a/text()"
    ).getall()
    foreword = response.xpath(
        "/html/body/div[5]/div/div/div[1]/div[1]/div[2]/div[3]/p//text()"
    ).getall()
    info = []
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(", ".join(types))
    info.extend(foreword)
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
    chapter = response.xpath('//*[@id="j_content"]/div[2]/h2/a/text()').get()
    # get content
    content = response.xpath('//*[@id="j_content"]/div[4]/div[1]//text()').getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
