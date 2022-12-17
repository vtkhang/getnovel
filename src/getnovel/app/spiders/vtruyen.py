"""Get novel from domain vtruyen.

.. _Web sites:
   https://vtruyen.com

"""
from pathlib import Path

import scrapy


class TruyenCvSubSpider(scrapy.Spider):
    """Define spider for domain: vtruyen"""

    name = "vtruyen"

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
        self.total_chapter = 0
        self.base_url = None

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
            response.xpath(
                '//div[@class="nh-thumb nh-thumb--210 shadow"]/img/@src'
            ).get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)  # get info and write it to save path
        total_chapter_str = response.xpath(
            '//*[@id="nav-tab-chap"]/span[2]/text()'
        ).get()
        if total_chapter_str is None:
            raise scrapy.exceptions.CloseSpider(
                reason="Can't get total chapter number"
            )
        try:
            total_chapter = int(total_chapter_str)
        except ValueError as e:
            raise scrapy.exceptions.CloseSpider(
                reason="Can't convert to integer"
            ) from e
        self.base_url = response.request.url
        self.total_chapter = total_chapter
        yield scrapy.Request(
            url=self.base_url + r"/chuong-" + str(self.start_chap),
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
        if (
            response.meta["id"] >= self.total_chapter
            or response.meta["id"] == self.stop_chap
        ):
            raise scrapy.exceptions.CloseSpider(reason="Done")

        yield scrapy.Request(
            url=self.base_url + r"/chuong-" + str(response.meta["id"] + 1),
            headers=response.headers,
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
    title = response.xpath('//h1[@class="h3 mr-2"]/a/text()').get()  # extract title
    author = response.xpath(
        '//ul[@class="list-unstyled mb-4"]/li[1]//text()'
    ).get()  # extract author
    types = response.xpath(
        '//ul[@class="list-unstyled mb-4"]//text()'
    ).getall()[2:]  # extract types
    foreword = response.xpath(
        '//div[@class="content"]/p/text()'
    ).getall()  # extract description
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
    chapter = response.xpath('//div[contains(@class,"nh-read__title")]/text()').get()
    # extract content
    content = response.xpath('//div[@id="js-read__content"]/text()').getall()
    content.insert(0, chapter)
    # write content to file
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
