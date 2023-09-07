"""Make EPUB module."""
import html
import logging
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from shutil import copy, copytree, move
from uuid import uuid1
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytz
from PIL import Image
from slugify import slugify

from getnovel import data
from getnovel.utils.file import XhtmlFileConverter

TEMPLATE = Path(files(data).joinpath("template"))

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level="INFO",
)
_logger = logging.getLogger(__name__)


class EpubMaker:
    """Make epub from raw directory."""

    def __init__(self: "EpubMaker", raw: Path, lang_code: str) -> None:
        """Assign raw directory.

        Parameters
        ----------
        raw : Path
            Raw directory.
        """
        self.raw = raw.resolve()
        self.raw_foreword = self.raw / "foreword.txt"
        self.epub = self.raw.parent / "epub"  # Epub directory
        self.epub_file: Path = None  # Epub file
        self.oebps = self.epub / "OEBPS"  # OEBPS directory
        self.text = self.oebps / "Text"  # Text directory
        self.images = self.oebps / "Images"  # Images directory
        self.cover = self.images / "cover.jpg"  # cover.jpg
        self.xhtml_cover = self.text / "cover.xhtml"  # cover.xhtml
        self.xhtml_nav = self.text / "nav.xhtml"  # nav.xhtml
        self.opf_content = self.oebps / "content.opf"  # content.opf
        self.ncx_toc = self.oebps / "ncx" / "toc.ncx"  # toc.ncx
        self.lang_code = lang_code  # Language code

    def process(self: "EpubMaker", **options: Path | str | bool | None) -> None:
        """Make epub.

        Parameters
        ----------
        options:
            result: Path | str | None
                Path of result directory.
            dedup: bool
                If specified, deduplicate chapter title.
        """
        self.epub_file = self.raw.parent
        if options.get("result"):
            self.epub_file = Path(options.get("result")).resolve()
        cvt = XhtmlFileConverter(raw=self.raw)
        cvt.process(dedup=options.get("dedup"), lang_code=self.lang_code)
        self.epub.mkdir(parents=True, exist_ok=True)
        self.__copy_to_epub(cvt.result)
        self.__make_epub()

    def __copy_to_epub(self: "EpubMaker", xhtml: Path) -> None:
        copytree(TEMPLATE, self.epub, dirs_exist_ok=True)
        (self.text / "c1.xhtml").unlink()
        self.cover.unlink()
        copytree(xhtml, self.text, dirs_exist_ok=True)
        move(self.text / "cover.jpg", self.images)

    def __make_epub(self: "EpubMaker") -> None:
        fw_lines = self.raw_foreword.read_text(encoding="utf-8").splitlines()
        novel_title = fw_lines[0]  # content.opf, toc.ncx, zip
        novel_uuid = uuid1()  # content.opf, toc.ncx
        publisher_name = "hacde"  # content.opf
        cover_title = "Ảnh bìa"  # cover.xhtml, toc.ncx
        nav_title = "Mục lục"  # nav.xhtml
        foreword_title = "Lời tựa"  # nav.xhtml, toc.ncx
        if self.lang_code == "zh":
            cover_title = "封面"
            nav_title = "目录"
            foreword_title = "前言"
        # edit cover.xhtml
        image = Image.open(self.cover)
        ext = image.format.lower()
        width, height = image.size
        image.save(self.cover, ext)
        image.close()
        self.cover.unlink()
        self.xhtml_cover.write_text(
            self.xhtml_cover.read_text(encoding="utf-8").format(
                cover_title=cover_title,
                width=width,
                height=height,
                ext=ext,
            ),
            encoding="utf-8",
        )
        # edit nav.xhtml
        nav_li_tag_list = []
        opf_item_tag_list = []
        opf_itemref_tag_list = []
        navpoint_tag_list = []
        nav_li = '    <li><a href="{chapter_name}">{chapter_title}</a></li>'
        item_tag = (
            '<item id="{chapter_id}" '
            'href="Text/{chapter_name}" media-type="application/xhtml+xml"/>'
        )
        itemref = '<itemref idref="{chapter_id}"/>'
        navpoint = (
            '  <navPoint id="navPoint{index}">\n'
            "      <navLabel>\n"
            "        <text>{chapter_title}</text>\n"
            "      </navLabel>\n"
            '      <content src="../Text/{chapter_name}" />\n'
            "  </navPoint>"
        )
        chapter_list = sorted(self.raw.glob("*[0-9].txt"), key=get_id)
        for chapter in chapter_list:
            title = chapter.read_text(encoding="utf-8").splitlines()[0]
            title = html.escape(title)
            name = chapter.with_suffix(".xhtml").name
            chapter_id = f"ID{name}"
            navpoint_tag_list.append(
                navpoint.format(
                    index=chapter.stem,
                    chapter_title=title,
                    chapter_name=name,
                ),
            )
            opf_item_tag_list.append(
                item_tag.format(chapter_name=name, chapter_id=chapter_id),
            )
            opf_itemref_tag_list.append(itemref.format(chapter_id=chapter_id))
            nav_li_tag_list.append(
                nav_li.format(chapter_name=name, chapter_title=title),
            )
        # write to nav.xhtml
        self.xhtml_nav.write_text(
            self.xhtml_nav.read_text(encoding="utf-8").format(
                language_code=self.lang_code,
                nav_title=nav_title,
                foreword_title=foreword_title,
                cover_title=cover_title,
                nav_li_tag_list="\n".join(nav_li_tag_list),
            ),
            encoding="utf-8",
        )
        # write to content.opf
        self.opf_content.write_text(
            self.opf_content.read_text(encoding="utf-8").format(
                novel_title=novel_title,
                author_name=fw_lines[1],
                language_code=self.lang_code,
                publisher_name=publisher_name,
                date_created=datetime.now(pytz.UTC).strftime("%Y-%m-%d"),
                date_modified=datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                novel_uuid=novel_uuid,
                ext=ext,
                opf_item_tag_list="\n    ".join(opf_item_tag_list),
                opf_itemref_tag_list="\n    ".join(opf_itemref_tag_list),
            ),
            encoding="utf-8",
        )
        # write to toc.ncx
        self.ncx_toc.write_text(
            self.ncx_toc.read_text(encoding="utf-8").format(
                novel_uuid=novel_uuid,
                novel_title=novel_title,
                foreword_title=foreword_title,
                navpoint_tag_list="\n".join(navpoint_tag_list),
            ),
            encoding="utf-8",
        )
        # zip files to epub
        epub_title = slugify(
            novel_title,
            max_length=32,
            word_boundary=True,
            save_order=True,
        )
        with ZipFile(
            self.epub_file / f"{epub_title}.epub",
            "w",
            compression=ZIP_DEFLATED,
            compresslevel=9,
        ) as f_zip:
            mime_path = self.epub / "mimetype"
            f_zip.write(
                mime_path,
                mime_path.relative_to(self.epub),
                compress_type=ZIP_STORED,
            )
            mime_path.unlink()
            for path in self.epub.rglob("*"):
                f_zip.write(path, path.relative_to(self.epub))
            copy(TEMPLATE / "mimetype", self.epub)
        _logger.info("Done making epub. View result at: %s", self.epub_file)


def get_id(path: Path) -> int:
    """Get chapter id."""
    return int(path.stem)
