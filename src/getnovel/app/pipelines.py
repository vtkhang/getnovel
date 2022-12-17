"""Define your item pipelines here

   Don't forget to add your pipeline to the ITEM_PIPELINES setting
   See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

   useful for handling different item types with a single interface
"""
from pathlib import Path

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from getnovel.app import items


class AppPipeline:
    """Define App pipeline."""

    def process_item(self, item: scrapy.Item, spider):
        """Process logic."""
        sp: Path = spider.save_path
        el = ""
        if type(item) == items.Info:
            sp = sp / "foreword.txt"
            el = "of novel info is empty"
        elif type(item) == items.Chapter:
            id = item.pop("id")
            sp = sp / f"{id}.txt"
            el = f"of chapter {item.get(id)} is empty"
        elif type(item) == items.CoverImage:
            return item
        else:
            raise scrapy.exceptions.DropItem("Invalid item detected!")
        r = []
        for k in item.keys():
            if item.get("k", "") == "":
                raise scrapy.exceptions.DropItem(f"Field {k} {el}")
            else:
                r.append(item[k])
        sp.write_text(data="\n".join(r), encoding="utf-8")
        return item


class CoverImagesPipeline(ImagesPipeline):
    """Define Image Pipeline"""

    def file_path(self, request, response=None, info=None, *, item=None):
        return str(info.spider.save_path / 'cover.jpg')
