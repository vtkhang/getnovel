"""Get novel from domain twpiaotian.

.. _Web site:
   https://www.twpiaotians.com

"""
from pathlib import Path

import scrapy


class TWpiaotianSpider(scrapy.Spider):
    """Define spider for domain: twpiaotian"""

    name = "twpiaotians"

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
            url=response.xpath('//a[@class="hover-img"]/img/@src').get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)
        t: str = response.request.url
        menu_link = "https://www.twpiaotians.com/piaotianlist/{0}/dir.html".format(
            t.rsplit("/", 1)[1].split("")[0]
        )
        yield scrapy.Request(
            url=menu_link,  # goto start chapter
            callback=self.parse_menu,
        )

    def parse_menu(self, response: scrapy.http.Response):
        """Extract table of content of the novel and
        get the link of start chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the start chapter page.
        """
        self.menu = response.xpath('//ul[@class="mulu_list clear"]/li/a/@href').getall()
        yield scrapy.Request(
            url="https://www.twpiaotians.com{0}".format(self.menu[self.start_chap - 1]),
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
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url="https://www.twpiaotians.com{0}".format(self.menu[response.meta["id"]]),
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
    title: str = response.xpath('//div[@class="bookintro"]/h2/text()').get()
    author = response.xpath('//div[@class="bookintro"]/h2/span/a/text()').get().strip()
    types = response.xpath(
        '//div[@class="bookintro"]/p[@class="label"]/span[2]/text()'
    ).getall()
    foreword = response.xpath(
        '//div[@class="bookintro"]/p[@class="intro"]/text()'
    ).getall()
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
    chapter = response.xpath('//div[@class="pt-read-title"]/h1/a/@title').get()
    # get content
    content: list = response.xpath(
        '//div[contains(@class,"pt-read-text")]/p/text()'
    ).getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
