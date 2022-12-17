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
    """Define App pipeline"""

    def process_item(self, item: scrapy.Item, spider):
        """Process logic"""
        sp: Path = spider.save_path
        el = ""
        fk = ""
        if type(item) == items.Info:
            sp = sp / "foreword.txt"
            el = "of novel info is empty"
            fk = ["images", "image_urls"]
        elif type(item) == items.Chapter:
            cid = item.get("id", "Unknown")
            sp = sp / f'{cid}.txt'
            el = f"of chapter {cid} is empty"
            fk = ["id"]
        else:
            raise scrapy.exceptions.DropItem("Invalid item detected!")
        r = []
        for k in item.keys():
            if item.get(k, "") == "":
                raise scrapy.exceptions.DropItem(f"Field {k} {el}")
            elif k not in fk:
                r.append(item[k])
        sp.write_text(data="\n".join(r), encoding="utf-8")
        return item


class CoverImagesPipeline(ImagesPipeline):
    """Define Image Pipeline"""

    def file_path(self, request, response=None, info=None, *, item=None):
        return str(info.spider.save_path / "cover.jpg")
