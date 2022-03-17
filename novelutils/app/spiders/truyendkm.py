"""Get novel from domain webtruyen.

.. _Web site:
   https://truyendkm.com

"""
from pathlib import Path
from typing import List

import scrapy


class WebTruyenSpider(scrapy.Spider):
    """Define spider for domain: truyendkm."""
    name = 'truyendkm'

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
        self.menu = []

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the menu.

        Args:
          response: the response to parse
          **kwargs: arbitrary keyword arguments

        Yields:
          scrapy.Request: request to the menu of novel

        """
        # get cover
        cover_link = response.xpath('//*[@class="book3d"]/img/@data-src').get()
        yield scrapy.Request(url=cover_link, callback=self.parse_cover)
        get_info(response, self.save_path)
        # get menu list
        self.menu.extend(response.xpath('//div[@id="dsc"]/ul[@class="listchap"]/li/a/@href').getall())
        # get next menu page
        n_menu_url: str = response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').get()
        # crawl next page
        if n_menu_url is not None and self.start_chap > len(self.menu):
            total_page_str: str = response.xpath('//ul[@class="pagination"]/li[last() - 1]/a/text()').get()
            if total_page_str is None:
                raise scrapy.exceptions.CloseSpider(reason='can\'t parse menu, can\'t get total menu pages')
            else:
                total_page = int(total_page_str)
                yield scrapy.Request(url=n_menu_url,
                                     callback=self.parse_menu,
                                     priority=total_page)
        else:
            yield scrapy.Request(
                url=self.menu[self.start_chap - 1],
                callback=self.parse_content,
                meta={'id': self.start_chap}
            )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Args:
          response: the response contains a binary image

        Returns:
          None

        """
        (self.save_path / 'cover.jpg').write_bytes(response.body)

    def parse_menu(self, response: scrapy.http.Response):
        """Extract link of the start chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the start chapter

        """
        self.menu.extend(response.xpath('//div[@id="dsc"]/ul[@class="listchap"]/li/a/@href').getall())
        t = response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').get()
        if t is None or t == '#' or self.start_chap <= len(self.menu):
            yield scrapy.Request(
                url=self.menu[self.start_chap - 1],
                callback=self.parse_content,
                meta={'id': self.start_chap})
        else:
            yield scrapy.Request(url=t,
                                 callback=self.parse_menu,
                                 priority=response.request.priority - 1)

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the next chapter

        """
        get_content(response, self.save_path)
        npu = response.xpath('//span[@class="pull-right"]/a/@href').get()
        if (npu is None) or response.meta['id'] == self.stop_chap:
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
    title = response.xpath('/html/body/div[5]/div[1]/div[1]/div/h1/text()').get()
    # get book info
    author = response.xpath('//*[@id="thong_tin"]/div/p[1]/span[2]/a/text()').get()
    types: List[str] = response.xpath('/html/body/div[4]/ol//a//text()').getall()[1:-2]
    foreword = response.xpath('//*[@id="gioi_thieu"]/div/text()').getall()
    info = list()
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    tmp = list()
    for item in types:
        tmp1 = item.strip()
        if tmp1 != '':
            tmp.append(tmp1)
    types = tmp
    info.append(', '.join(types))
    info.extend(foreword)
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
    chapter_index: str = response.xpath("/html/body/div[5]/div/div/div/div/h2/text()").get()
    chapter_name: str = response.xpath("/html/body/div[5]/div/div/div/div/h1/text()").get()
    chapter = f'{chapter_index.strip()} : {chapter_name.strip()}'
    # get content
    content = response.xpath('/html/body/div[5]/div/div/div/div/div[2]/text()').getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        '\n'.join([x.strip() for x in content if x.strip() != '']),
        encoding='utf-8'
    )
