"""Get novel on domain tangthuvien.

.. _Web site:
   https://truyen.tangthuvien.vn

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TangThuVienSpider(Spider):
    """Define spider for domain: tangthuvien"""

    name = "tangthuvien"

    def __init__(
        self,
        u: str,
        n: int,
        i: int = 1,
        s: int = 1,
        *args,
        **kwargs,
    ):
        """Initialize attributes.

        Parameters
        ----------
        u : str
            Url of the start chapter.
        n : int
            Amount of chapters need to be crawled, input -1 to get all chapters.
        i : int
            Skip info page if value is 0.
        s : int
            Begin value for file name id.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u]
        self.s = int(s)
        self.n = int(n) + self.s
        self.i = int(i)
        self.toc = []
        self.toc_len = 0

    def parse(self, response: Response):
        """Extract info and send request to table of content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        Request
            Request to table of content.
        """
        yield get_content(response, self.s)
        sid = response.xpath("//div[4]//input[3]/@value").get()
        yield response.follow(
            url=f"/story/chapters?story_id={sid}",
            callback=self.parse_next,
        )
        if self.i != 0:
            self.i = 0
            yield Request(url=response.url.rsplit("/", 1)[0], callback=self.parse_info)

    def parse_next(self, response: Response):
        """Extract link of the next chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the next chapter.
        """
        self.toc.extend([i.strip() for i in response.xpath("//a/@href").getall()])
        self.toc_len = len(self.toc)
        cur_chap = 0
        for index in range(len(self.toc)):
            if self.toc[index] == self.start_urls[0]:
                cur_chap = index
        if cur_chap + 1 == self.toc_len:
            raise CloseSpider(reason="Done")
        yield Request(
            url=self.toc[cur_chap + 1],
            meta={
                "id": self.s + 1,
                "cur_chap": cur_chap + 2,
            },
            callback=self.parse_content,
        )

    def parse_content(self, response: Response):
        """Extract content.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Chapter
            Chapter item.
        Request
            Request to the next chapter.
        """
        yield get_content(response, response.meta["id"])
        if (response.meta["id"] == self.n) or (
            response.meta["cur_chap"] == self.toc_len
        ):
            raise CloseSpider(reason="Done")
        yield Request(
            url=self.toc[response.meta["cur_chap"]],
            meta={
                "id": response.meta["id"] + 1,
                "cur_chap": response.meta["cur_chap"] + 1,
            },
            callback=self.parse_content,
        )

    def parse_info(self, response: Response):
        """Extract info.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Info
            Info item.
        """
        yield get_info(response)


def get_info(response: Response) -> Info:
    """Get novel information.

    Parameters
    ----------
    response : Response
        The response to parse.

    Returns
    -------
    Info
        Populated Info item.
    """
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", "//div[5]//h1/text()")
    r.add_xpath("author", "//div[5]//div[2]/p[1]/a[1]/text()")
    r.add_xpath("types", "//div[5]//div[2]/p[1]/a[2]/text()")
    r.add_xpath("foreword", '//div[@class="book-intro"]/p/text()')
    r.add_xpath("image_urls", '//*[@id="bookImg"]/img/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response, id: int) -> Chapter:
    """Get chapter content.

    Parameters
    ----------
    response : Response
        The response to parse.

    id: int
        File name id.
    Returns
    -------
    Chapter
        Populated Chapter item.
    """
    r = ChapterLoader(item=Chapter(), response=response)
    r.add_value("id", str(id))
    r.add_value("url", response.url)
    r.add_xpath("title", "//div[5]//h2/text()")
    r.add_xpath("content", '//div[contains(@class,"box-chap")]//text()')
    return r.load_item()
