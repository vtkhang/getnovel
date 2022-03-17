"""Get novel from domain truyenfull.

.. _Web site:
   https://truyenfull.vn

"""
from pathlib import Path

import scrapy


class TruyenFullSpider(scrapy.Spider):
    """Define spider for domain: truyenfull."""
    name = 'truyenfull'

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
        # download cover
        yield scrapy.Request(url=response.xpath(
            '//div[@class="book"]/img[@itemprop="image"]/@src').get(),
                             callback=self.parse_cover)
        get_info(response, self.save_path)
        yield scrapy.Request(
            url=response.url + 'chuong-' + str(self.start_chap),  # goto start chapter
            meta={'id': 1},
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
        link_next_chap = response.xpath('//a[@id="next_chap"]/@href').getall()[0]
        if ('javascript:void(0)' in link_next_chap) or response.meta['id'] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason='Done')
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
    title = response.xpath('//*[@id="truyen"]/div[1]/div[1]/h3/text()').get()
    author = response.xpath('//*[@id="truyen"]/div[1]/div[1]/div[2]/div[2]/div[1]/a/text()').get()
    types = response.xpath('//*[@id="truyen"]/div[1]/div[1]/div[2]/div[2]/div[2]/a/text()').getall()
    foreword = response.xpath('//*[@id="truyen"]/div[1]/div[1]/div[3]/div[2]//text()').getall()
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
    # get chapter
    chapter = ('Chương ' + response.xpath('/html//a[@class="chapter-title"]/text()').get())
    # get content
    content = response.xpath('/html//div[@id="chapter-c"]/text()').getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        '\n'.join([x.strip() for x in content if x.strip() != '']),
        encoding='utf-8'
    )
