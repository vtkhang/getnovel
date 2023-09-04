"""Define here the models for your scraped items.

.. _See documentation in:
   https://docs.scrapy.org/en/latest/topics/items.html

"""

from scrapy import Field, Item


class Info(Item):
    """Store info."""

    title = Field()
    author = Field()
    types = Field()
    foreword = Field()
    url = Field()
    image_urls = Field()
    images = Field()


class Chapter(Item):
    """Store chapter."""

    index = Field()
    url = Field()
    title = Field()
    content = Field()
