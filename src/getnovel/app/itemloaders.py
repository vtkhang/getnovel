"""Define item loaders.

.. _See documentation in:
   https://docs.scrapy.org/en/latest/topics/loaders.html

"""

from itemloaders.processors import Identity, Join, MapCompose
from scrapy.loader import ItemLoader


def filter_blank(v: str | None) -> str | None:
    """Remove blank lines."""
    return v


class InfoLoader(ItemLoader):
    r"""Process info data.

    Examples
    --------
    >>> after_process = {
        "title": "XpathResult1 XpathResult2 ...",
        "author": "XpathResult1 XpathResult2 ...",
        "types": "XpathResult1, XpathResult2, ...",
        "foreword": "XpathResult1\\nXpathResult2\\n...",
        "url": "url_str"
        "image_urls": ["XpathResult1", "XpathResult2",...],
        "images": "AUTO_GENERATED_BY_IMAGEPIPLINE"
    }
    """

    default_input_processor = MapCompose(str.strip, filter_blank)
    default_output_processor = Join()
    types_out = Join(", ")
    foreword_out = Join("\n")
    image_urls_out = Identity()
    images_out = Identity()


class ChapterLoader(ItemLoader):
    r"""Process chapter data.

    Examples
    --------
    >>> after_process = {
        "id": "1",
        "url": "url_str",
        "title": "XpathResult1 XpathResult2 ...",
        "content": "XpathResult1\\nXpathResult2\\n..."
    }
    """

    default_input_processor = MapCompose(str.strip, filter_blank)
    default_output_processor = Join()
    content_out = Join("\n")
