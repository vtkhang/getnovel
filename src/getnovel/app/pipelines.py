"""Define your item pipelines here

   Don't forget to add your pipeline to the ITEM_PIPELINES setting
   See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

   useful for handling different item types with a single interface
"""
import logging
from pathlib import Path

import scrapy
from getnovel.app.items import Info, Chapter, Image

_logger = logging.getLogger(__name__)


class AppPipeline:
    """Define App pipeline."""

    def process_item(self, item: scrapy.Item, spider):
        """Process logic."""
        sp: Path = spider.save_path
        el = ""
        if type(item) == Info:
            sp = sp / "foreword.txt"
            el = "of novel info is empty"
        elif type(item) == Chapter:
            id = item.pop("id")
            sp = sp / f"{id}.txt"
            el = f"of chapter {item.get(id)} is empty"
        elif type(item) == Image:
            (sp / "cover.jpg").write_bytes(item.get("content"))
            return item
        else:
            _logger.error("Invalid item detected!")
        r = []
        for k in item.keys():
            if item[k] == "":
                _logger.error(f"Field {k} {el}")
                raise scrapy.exceptions.DropItem(reason="Empty field Detected!")
            else:
                r.append(item[k])
        sp.write_text(data="\n".join(r), encoding="utf-8")
        return item
