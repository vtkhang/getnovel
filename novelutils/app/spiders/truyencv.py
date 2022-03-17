"""Get novel from domain truyencv, metruyenchu, nuhiep, vtruyen.

.. _Web sites:
   https://truyencv.com

"""
from pathlib import Path

import scrapy


class TruyenCvSpider(scrapy.Spider):
    """Define spider for domain: truyencv, metruyenchu, nuhiep, vtruyen."""
    name = 'truyencv'

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
        # download cover
        yield scrapy.Request(
            response.xpath('//*[@class="truyencv-detail-info-block"]//img/@src').get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)  # get info and write it to save path
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        yield scrapy.FormRequest(
            method='POST',
            url='https://truyencv.com/index.php',
            headers=headers,
            formdata=get_formdata(response),
            callback=self.parse_link
        )

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Args:
          response: the response contains a binary image

        Returns:
          None

        """
        (self.save_path / 'cover.jpg').write_bytes(response.body)

    def parse_link(self, response: scrapy.http.Response):
        """
        Extract menu of the novel and get the link of start chapter.
        Args:
            response: Selector for response.

        Yields:
            scrapy.Request: request to start chapter
        """
        self.menu.extend([x.strip() for x in response.xpath('//*[@class="item"]/a/@href').getall()])
        self.menu = list(dict.fromkeys(self.menu))
        self.menu.reverse()
        chapter = self.menu[self.start_chap - 1]
        yield scrapy.Request(url=chapter,
                             meta={
                                 'id': self.start_chap
                             },
                             callback=self.parse_content
                             )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Args:
          response: the response to parse

        Yields:
          scrapy.Request: request to the next chapter

        """
        get_content(response, self.save_path)
        if (response.meta['id'] == len(self.menu)) or response.meta['id'] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason='Done')

        yield scrapy.Request(url=self.menu[response.meta['id']],
                             headers=response.headers,
                             meta={
                                 'id': response.meta['id'] + 1
                             },
                             callback=self.parse_content)


def get_info(response: scrapy.http.Response, save_path: Path):
    """Get info of this novel.

    Args:
      response: the response to parse
      save_path: path to raw data folder

    Returns:
      None

    """
    # extract info
    title = response.xpath('//*[@class="title"]/a/text()').get()  # extract title
    author = response.xpath('//div[@class="truyencv-detail-info-block"]//div[@class="info"]//div[@class="list"]//div'
                            '[@class="item-value"]/a/text()').get()  # extract author
    types = response.xpath('//ul[@class="list-unstyled categories"]//a/text()').getall()  # extract types
    foreword = response.xpath('//div[@class="brief"]/p/text()').getall()  # extract description
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
    # extract chapter title
    chapter = response.xpath('//h2[@class="title"]/text()').get()
    # extract content
    content = response.xpath('//div[@class="content"]//text()').getall()
    content.insert(0, chapter)
    # write content to file
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        '\n'.join([x.strip() for x in content if x.strip() != '']),
        encoding='utf-8'
    )


def get_formdata(rs: scrapy.http.Response):
    """Extract data for form data.

    Args:
        rs: http response

    Returns:
        dict contains data
    """
    t = rs.xpath('//*[@role="presentation"]/a/@onclick').get()
    t1 = t.replace('showChapter(', '').replace('\'', '').replace(')', '').split(',')
    return {
        'showChapter': '1',
        'media_id': t1[0],
        'number': t1[1],
        'page': t1[2],
        'type': t1[3]
    }
