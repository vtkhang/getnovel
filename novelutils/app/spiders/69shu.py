"""Get novel from domain uukanshu.

.. _Web site:
   https://www.69shu.com/

"""
from pathlib import Path

import scrapy


class SixNineshuSpider(scrapy.Spider):
    """Define spider for domain: 69shu."""
    name = '69shu'

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
        self.menu: list = list()

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the menu.

        Args:
          response: the response to parse
          **kwargs: arbitrary keyword arguments

        Yields:
          scrapy.Request: request to the menu of novel

        """
        # download cover
        yield scrapy.Request(
            url='https://www.69shu.com{0}'.format(response.xpath('//*[@class="bookimg2"]/img/@src').get()),
            callback=self.parse_cover
        )
        get_info(response, self.save_path)
        menu_link = 'https://www.69shu.com{0}'.format(response.xpath('//*[@class="btn more-btn"]/@href').get())
        yield scrapy.Request(
            url=menu_link,
            callback=self.parse_menu
        )

    def parse_menu(self, response: scrapy.http.Response):
        self.menu: list = response.xpath('//*[@id="catalog"]/ul/li/a/@href').getall()
        if self.start_chap > len(self.menu):
            raise scrapy.exceptions.CloseSpider(reason='Start chapter index is greater than menu list.')
        yield scrapy.Request(
            url=self.menu[self.start_chap - 1],  # goto start chapter
            meta={'id': self.start_chap},
            callback=self.parse_content,
        )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Args:
          response: the response contains a binary image

        Returns:
          None

        """
        (self.save_path / 'cover.jpg').write_bytes(response.body)

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the next chapter

        """
        get_content(response, self.save_path)
        if (response.meta['id'] == len(self.menu)) or (response.meta['id'] == self.stop_chap):
            raise scrapy.exceptions.CloseSpider(reason='Done')
        link_next_chap = self.menu[response.meta['id']]
        response.request.headers[b'Referer'] = [str.encode(response.url)]
        yield scrapy.Request(
            url=link_next_chap,
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
    # extract info
    title: str = response.xpath('//*[@class="booknav2"]/h1/a/text()').get()
    author: str = response.xpath('//*[@class="booknav2"]/p/a/text()').get()
    types = ['--']
    foreword = ['--']
    info = list()
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(', '.join(types))
    info.extend(foreword)
    # write info to file
    (save_path / 'foreword.txt').write_text(
        '\n'.join(info),
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
    # # get chapter
    # chapter = response.xpath('//h1[@class="hide720"]/text()').get()
    # if '.' in chapter:
    #     chapter = chapter.rsplit('.', 1)[1]
    # get content
    content: list = response.xpath(
        '//*[@class="txtnav"]//text()[not(parent::h1) and not(parent::span) and not(parent::script)]'
    ).getall()
    # content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        '\n'.join([x.strip() for x in content if x.strip() != '']),
        encoding='utf-8'
    )
