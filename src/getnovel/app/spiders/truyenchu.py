"""Get novel on domain truyenchu.

.. _Web site:
   https://truyenchu.vn/

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class TruyenChuSpider(Spider):
    """Define spider for domain: truyenchu"""

    name = "truyenchu"

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

    def parse(self, response: Response):
        """Extract content, send request to next chapter.
        Send request to info page.

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
        Request
            Request to the novel info page.
        """
        yield get_content(response, self.s)
        next_url = response.xpath('//a[@id="next_chap"]/@href').get()
        if (next_url == "#") or (self.s == self.n):
            raise CloseSpider(reason="Done")
        self.s += 1
        yield response.follow(
            url=next_url,
            callback=self.parse,
        )
        if self.i != 0:
            self.i = 0
            yield Request(url=response.url.rsplit("/", 1)[0], callback=self.parse_info)

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
    imgurl = response.xpath('//div[@class="book"]/img/@src').get()
    r = InfoLoader(item=Info(), response=response)
    r.add_xpath("title", '//h1[@class="story-title"]/a/text()')
    r.add_xpath("author", '//*[@itemprop="author"]//span/text()')
    r.add_xpath("types", '//*[@id="truyen"]//div[1]//div[1]/div[3]/a/text()')
    r.add_xpath("foreword", '//*[@id="truyen"]/div[1]/div[2]/div[2]/div[2]//text()')
    r.add_value("image_urls", response.urljoin(imgurl))
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
    r.add_xpath("title", '//a[@class="chapter-title"]//text()')
    r.add_xpath("content", '//div[@id="chapter-c"]//text()[not(parent::script)]')
    return r.load_item()
