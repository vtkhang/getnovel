"""Define your item pipelines here

   Don't forget to add your pipeline to the ITEM_PIPELINES setting
   See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

   useful for handling different item types with a single interface
"""

import logging
from pathlib import Path

from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from getnovel.app.items import Info, Chapter

_logger = logging.getLogger(__name__)


class AppPipeline:
    """Define App pipeline"""

    def process_item(self, item, spider):
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
        for k in item.keys():
            if item.get(k) == "" or item.get(k) is None:
                raise DropItem(f"Field {k} is empty!")
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
                (sp / f"{item['id']}.txt").write_text(
                    data="\n".join(r), encoding="utf-8"
                )
            else:
                raise DropItem("Invalid item detected!")
        except KeyError as key:
            _logger.warning(f"Error url: {item.get('url', 'Field url is not exist!')}")
            raise DropItem(f"Field {key} is not exist!")
        return item


class CoverImagesPipeline(ImagesPipeline):
    """Define Image Pipeline"""

    def file_path(self, request, response=None, info=None, *, item=None):
        """Customize save path for cover image."""
        return str(Path(info.spider.settings["RESULT"]) / "cover.jpg")
