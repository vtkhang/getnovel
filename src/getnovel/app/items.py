"""Define here the models for your scraped items

.. _See documentation in:
   https://docs.scrapy.org/en/latest/topics/items.html

"""

from scrapy import Field, Item
from itemloaders.processors import MapCompose, Identity, Join
from scrapy.loader import ItemLoader


class Info(Item):
    """Store novel info."""

    title = Field()
    author = Field()
    url = Field()
    types = Field()
    foreword = Field()
    cover_url = Field()
    save_path = Field()


class InfoLoader(ItemLoader):
    """Process info data"""

    default_input_processor = MapCompose(str.strip)
    default_output_processor = Join(" ")

    def types_out(self, values):
        return ", ".join(values)

    def foreword_out(self, values):
        return "\n".join(values)

    save_path_in = Identity()
    save_path_out = Identity()


class Chapter(Item):
    """Store novel chapters."""

    title = Field()
    content = Field()


class ChapterLoader(ItemLoader):
    """Process chapter data"""

    default_input_processor = MapCompose(str.strip)

    def title_out(self, values):
        return " ".join(values)

    def content_out(self, values):
        return "\n".join([x for x in values if x != ""])
