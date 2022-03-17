"""Get novel from domain webtruyen.

.. _Web site:
   https://webtruyen.com

"""
from pathlib import Path

import scrapy


class WebTruyenSpider(scrapy.Spider):
    """Define spider for domain: webtruyen."""
    name = 'webtruyen'

    def __init__(self, url: str, save_path: Path, start_chap: int, stop_chap: int, *args, **kwargs):
        """Initialize the attributes for this spider.

        Args:
          url: full web site to novel info page
          save_path: path to raw directory
          start_chap: start chapter index
          stop_chap: stop chapter index, input -1 to get all chapters
          *args: variable length argument list
          **kwargs: arbitrary keyword arguments

        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.save_path = save_path
        self.start_chap = start_chap
        self.stop_chap = stop_chap

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the menu.

        Args:
          response: the response to parse
          **kwargs: arbitrary keyword arguments

        Yields:
          scrapy.Request: request to the menu of novel

        """
        # get cover
        cover_link = response.xpath('//*[@class="thumb"]/img[1]/@src').get()
        yield scrapy.Request(url=cover_link, callback=self.parse_cover)
        get_info(response, self.save_path)
        total_chap = 30
        # calculate the position of start_chap in menu list
        menu_page_have_start_chap = self.start_chap // total_chap + 1
        pos_of_start_chap_in_menu = self.start_chap % total_chap
        if pos_of_start_chap_in_menu == -1:
            menu_page_have_start_chap -= 1
            pos_of_start_chap_in_menu = total_chap
        pos_of_start_chap_in_menu -= 1  # because list in python have index begin with 0
        # check if the start_chap is outside available menu pages:
        total_page_str: str = response.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()').get()
        total_page = 1
        if total_page_str is not None:
            total_page = int(total_page_str)
        if menu_page_have_start_chap > total_page:
            scrapy.exceptions.CloseSpider(reason='start chapter is outside menu pages.')
        # Get menu list:
        t = response.xpath('//*[@id="chapters"]/ul/li/a/@href').getall()
        # check if the start_chap is outside available menu list
        if pos_of_start_chap_in_menu >= len(t) - 1:
            raise scrapy.exceptions.CloseSpider(reason='Start chapter not exist.')
        yield scrapy.Request(
            url='{0}{1}/'.format(response.url, str(menu_page_have_start_chap)),
            meta={'pos_start': pos_of_start_chap_in_menu},
            callback=self.parse_start
        )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Args:
          response: the response contains a binary image

        Returns:
          None

        """
        (self.save_path / 'cover.jpg').write_bytes(response.body)

    def parse_start(self, response: scrapy.http.Response):
        """Extract link of the start chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the start chapter

        """
        t = response.xpath('//*[@id="chapters"]/ul/li/a/@href').getall()
        yield scrapy.Request(
            url=t[response.meta['pos_start']],
            callback=self.parse_content,
            meta={'id': self.start_chap}
        )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the next chapter

        """
        get_content(response, self.save_path)
        npu = response.xpath('//*[@title="Chương Sau"]/@href').get()
        if (npu == '#') or response.meta['id'] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason='Done')
        response.request.headers[b'Referer'] = [str.encode(response.url)]
        yield scrapy.Request(
            url=npu,
            headers=response.request.headers,
            meta={'id': response.meta['id'] + 1},
            callback=self.parse_content,
        )


def get_info(response: scrapy.http.Response, save_path: Path):
    """Get info of this novel.

    Args:
      response: the response to parse
      save_path: path to raw data folder

    Returns:
      None

    """
    # get title
    title = response.xpath('//*[@id="story-detail"]/div[2]/h1/text()').get()
    # get book info
    author = response.xpath('//*[contains(@href,"tac-gia")]/text()').get()
    types = response.xpath('//*[@id="story-detail"]/div[1]/div[2]/p[2]/span/a/text()').getall()
    foreword = rm_tag(response.xpath('//*[@id="story-detail"]/div[2]/div[3]').get())
    info = list()
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(', '.join(types))
    info.extend(foreword.split('\n'))
    (save_path / 'foreword.txt').write_text(
        '\n'.join([x.replace('\n', ' ') for x in info]),
        encoding='utf-8'
    )


def get_content(response: scrapy.http.Response, save_path: Path):
    """Get title and content of chapter.

    Args:
      response: the response to parse
      save_path: path to raw directory

    Returns:
      None

    """
    chapter = response.xpath('//h2[@class="chapter-title"]/text()').get()
    # get content
    content = response.xpath('//div[@id="chapter-content"]/text()').getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        '\n'.join([x.strip() for x in content if x.strip() != '']),
        encoding='utf-8'
    )


def rm_tag(u: str):
    x = u.replace('<br>', '\n').replace('<br/>', '\n')
    r = []
    g = True
    for i in range(len(x)):
        if x[i] == '<':
            g = False
        if x[i] == '>':
            g = True
            continue
        if g is True:
            r.append(x[i])
    return ''.join(r)
