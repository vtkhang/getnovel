"""Define item loaders

.. _See documentation in:
   https://docs.scrapy.org/en/latest/topics/loaders.html

"""

from itemloaders.processors import MapCompose, Join, Identity
from scrapy.loader import ItemLoader


def filter_blank(v):
    if v is not None:
        return v


class InfoLoader(ItemLoader):
    """Process info data"""

    default_input_processor = MapCompose(filter_blank, str.strip)
    default_output_processor = Join()
    types_out = Join(", ")
    foreword_out = Join("\n")
    image_urls_out = Identity()
    images_out = Identity()


class ChapterLoader(ItemLoader):
    """Process chapter data"""

    default_input_processor = MapCompose(filter_blank, str.strip)
    default_output_processor = Join()
    content_out = Join("\n")
