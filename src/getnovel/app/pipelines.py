"""Define your item pipelines here.

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

useful for handling different item types with a single interface
"""

import logging
from pathlib import Path
from shutil import copy

from scrapy import Item, Spider
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from getnovel.app.items import Chapter, Info

_logger = logging.getLogger(__name__)


class AppPipeline:
    """Define App pipeline."""

    def process_item(self: "AppPipeline", item: Item, spider: Spider) -> Item:
        """Store items to files.

        Parameters
        ----------
        item : Item
            Input item.
        spider : Spider
            The spider that scraped input item.

        Returns
        -------
        Item
            Return item for another pipelines.

        Raises
        ------
        DropItem
            If item contains empty fields.
        DropItem
            If any field is not exists.
        DropItem
            Invalid item detected.
        """
        sp = Path(spider.settings["RESULT"])
        r = []
        for k in item:
            if item.get(k) == "" or item.get(k) is None:
                msg = f"Field {k} is empty!"
                raise DropItem(msg)
        try:
            if isinstance(item, Info):
                r.append(item["title"])
                r.append(item["author"])
                r.append(item["types"])
                r.append(item["url"])
                r.append(item["foreword"])
                (sp / "foreword.txt").write_text(data="\n".join(r), encoding="utf-8")
            elif isinstance(item, Chapter):
                r.append(item["title"])
                r.append(item["content"])
                (sp / f"{item['index']}.txt").write_text(
                    data="\n".join(r),
                    encoding="utf-8",
                )
            else:
                msg = "Invalid item detected!"
                raise DropItem(msg)
        except KeyError as key:
            _logger.warning("Error url: %s", item.get("url", "Field url is not exist!"))
            msg = f"Field {key} is not exist!"
            raise DropItem(msg) from KeyError
        return item


class CoverImagesPipeline(ImagesPipeline):
    """Define Image Pipeline."""

    def item_completed(self: "CoverImagesPipeline", results, item, info):
            print(type(item))
            return super().item_completed(results, item, info)

