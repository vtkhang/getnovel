"""This is the next generation spider for bachngocsach.

   This spider will start crawling from chapter page instead of novel info page.
   So we can easily make request to next chapter and info page instead of caculating start chapter
   and make request to table of content.

.. _Web site:
   https://bachngocsach.com.vn/reader

"""

from scrapy import Spider
from scrapy.http import Response, Request
from scrapy.exceptions import CloseSpider

from getnovel.app.items import Info, Chapter
from getnovel.app.itemloaders import InfoLoader, ChapterLoader


class BachNgocSachSpider(Spider):
    """Define spider for domain: bachngocsach

    Examples
    --------
    >>> scrapy crawl next_gen_spider `
        -a url=https://bachngocsach.com.vn/reader/truong-sinh-do-convert/nhqj `
        -a n=2
    """

    name = "next_gen_spider"

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
        url : str
            Url of the start chapter.
        n : int
            Amount of chapters need to be crawled, input -1 to get all chapters.
        i : int
            If is 0 then skip info page.
        s : int
            Begin value for file name id.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u]
        self.n = n+s
        self.s = int(s)
        self.i = int(i)

    def parse(self, response: Response):
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
        Request
            Request to the novel info page.
        """
        yield get_content(response, self.s)
        next_url = response.xpath('//a[contains(@class,"page-next")]/@href').get()
        if not next_url or self.s == self.n:
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

    Examples
    --------
    >>> before_process_by_loader = {
        "title": ["XpathResult1", "XpathResult2",...],
        "author": ["XpathResult1", "XpathResult2",...],
        "types": ["XpathResult1", "XpathResult2",...],
        "foreword": ["XpathResult1", "XpathResult2",...],
        "image_urls": ["XpathResult1", "XpathResult2",...],
        "images": "AUTO_GENERATED_BY_IMAGEPIPLINE"
    }

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
    r.add_xpath("title", '//*[@id="truyen-title"]/text()')
    r.add_xpath("author", '//div[@id="tacgia"]/a/text()')
    r.add_xpath("types", '//div[@id="theloai"]/a/text()')
    r.add_xpath("foreword", '//div[@id="gioithieu"]/div/p/text()')
    r.add_xpath("image_urls", '//div[@id="anhbia"]/img/@src')
    r.add_value("url", response.request.url)
    return r.load_item()


def get_content(response: Response, id: int) -> Chapter:
    """Get chapter content.

    Examples
    --------
    >>> before_process_by_loader = {
        "title": ["XpathResult1", "XpathResult2",...],
        "content": ["XpathResult1", "XpathResult2",...]
    }

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
    r.add_xpath("title", '//h1[@id="chuong-title"]/text()')
    r.add_xpath(
        "content",
        '//div[@id="noi-dung"]/p/text()',
    )
    r.add_value("id", str(response.meta["id"]))
    return r.load_item()
