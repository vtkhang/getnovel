"""Make EPUB module."""
import logging
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from shutil import copy, move
from uuid import uuid1
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from PIL import Image

from getnovel import data
from getnovel.utils.crawler import NovelCrawler
from getnovel.utils.file import FileConverter
from getnovel.utils.typehint import ListPath

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level="INFO",
)
_logger = logging.getLogger(__name__)


class EpubMaker:
    """Support making epub from input url or from a raw directory path."""

    def __init__(self, result: Path):
        """Assign path for the result directory.

        Parameters
        ----------
        result : Path
            Path of the result directory.
        """
        self.rp = result
        self.raw = self.rp / "raw"
        self.xhtml = self.rp / "xhtml"
        self.xhtml.mkdir(exist_ok=True, parents=True)
        self.epub = self.rp / "epub"
        self.epub.mkdir(exist_ok=True, parents=True)

    def from_url(
        self,
        url: str,
        dedup: bool,
        start: int,
        stop: int,
    ) -> None:
        """Get novel on website, zip them to epub.

        Parameters
        ----------
        url : str
            Url of the novel information page.
        dedup : bool
            If specified, deduplicate chapter title.
        start : int
            Start crawling from this chapter.
        stop : int
            Stop crawling after this chapter, input -1 to get all chapters.
        """
        # Get novel on web site.
        p = NovelCrawler(url=url)
        p.crawl(
            rm=True,
            start=start,
            stop=stop,
            clean=True,
            result=self.raw,
        )
        # convert to xhtml
        c = FileConverter(self.raw, self.xhtml)
        c.convert_to_xhtml(
            dedup=dedup,
            rm=True,
            lang_code=p.get_langcode(),
        )
        # copy epub template and then copy all files converted to epub directory
        self._copy_to_epub()
        # make epub
        self._make_epub(list(c.get_file_list("xhtml")), p.get_langcode())

    def from_raw(self, raw: Path, dedup: bool, lang_code: str) -> None:
        """Convert chapters from raw directory to xhtml then make epub.

        Parameters
        ----------
        raw : Path
            Path of the raw directory.
        dedup : bool
            If specified, deduplicate chapter title.
        lang_code : str
            Language code of the novel.
        """
        self.raw = raw
        c = FileConverter(raw, self.xhtml)
        c.convert_to_xhtml(
            dedup=dedup,
            rm=True,
            lang_code=lang_code,
        )
        # copy epub template and then copy all files converted to epub directory
        self._copy_to_epub()
        # make epub2
        self._make_epub(list(c.get_file_list("xhtml")), lang_code)

    def _copy_to_epub(self):
        # copy template epub to temp epub directory
        copytree_hm(Path(str(files(data).joinpath("template"))), self.epub)
        self.epub.chmod(0o0400 | 0o0200)
        # remove template file c1.xhtml in temp epub directory
        (self.epub / "OEBPS" / "Text" / "c1.xhtml").unlink()
        # copy files from xhtml directory to temp epub directory
        copytree_hm(self.xhtml, self.epub / "OEBPS" / "Text")
        # move cover image from ./OEBPS/Text to ./OEBPS/Images
        (self.epub / "OEBPS" / "Images" / "cover.jpg").unlink()
        move(
            str(self.epub / "OEBPS" / "Text" / "cover.jpg"),
            self.epub / "OEBPS" / "Images",
        )

    def _make_epub(self, xhtml_files: ListPath, lang_code: str):
        tp = self.epub / "OEBPS" / "Text"
        # Shared variable
        fw_lines = (tp / "foreword.xhtml").read_text(encoding="utf-8").splitlines()
        novel_title = fw_lines[12][6:-5]  # content.opf, toc.ncx, zip
        novel_uuid = uuid1()  # content.opf, toc.ncx
        publisher_name = "hacde"  # content.opf
        cover_title = "Ảnh bìa"  # cover.xhtml, toc.ncx
        nav_title = "Mục lục"  # nav.xhtml
        foreword_title = "Lời tựa"  # nav.xhtml, toc.ncx
        if lang_code == "zh":
            cover_title = "封面"
            nav_title = "目录"
            foreword_title = "前言"
        # edit cover.xhtml
        cp = tp / "cover.xhtml"  # cover path
        cip = tp.parent / "Images" / "cover.jpg"  # cover image path
        ci = Image.open(str(cip))  # cover image
        ext = ci.format.lower()  # extension of cover image
        width, height = ci.size  # get width and height
        ci.close()
        cip.rename(cip.with_suffix(f".{ext}"))  # rename cover image extension
        cp.write_text(
            cp.read_text(encoding="utf-8").format(
                cover_title=cover_title,
                width=width,
                height=height,
                ext=ext,
            ),
            encoding="utf-8",
        )
        # edit nav.xhtml, toc.ncx and content.opf
        # define paths
        np = tp / "nav.xhtml"  # nav.xhtml path
        op = tp.parent / "content.opf"  # content.opf path
        ncxp = tp.parent / "ncx" / "toc.ncx"  # toc.ncx path
        # create tag list
        nav_li_tag_list = []
        opf_item_tag_list = []
        opf_itemref_tag_list = []
        navpoint_tag_list = []
        nav_li = '    <li><a href="{chapter_name}">{chapter_title}</a></li>'
        item_tag = (
            '<item id="{chapter_name}" '
            'href="Text/{chapter_name}" media-type="application/xhtml+xml"/>'
        )
        itemref = '<itemref idref="{chapter_name}"/>'
        navpoint = (
            '  <navPoint id="navPoint{index}">\n'
            "      <navLabel>\n"
            "        <text>{chapter_title}</text>\n"
            "      </navLabel>\n"
            '      <content src="../Text/{chapter_name}" />\n'
            "  </navPoint>"
        )
        index = 2
        for item in xhtml_files[2:]:
            chapter_title = item.read_text(encoding="utf-8").splitlines()[5][9:-8]
            chapter_name = item.name
            navpoint_tag_list.append(
                navpoint.format(
                    index=str(index),
                    chapter_title=chapter_title,
                    chapter_name=chapter_name,
                ),
            )
            opf_item_tag_list.append(item_tag.format(chapter_name=chapter_name))
            opf_itemref_tag_list.append(itemref.format(chapter_name=chapter_name))
            nav_li_tag_list.append(
                nav_li.format(chapter_name=chapter_name, chapter_title=chapter_title),
            )
            index = index + 1
        # write to nav.xhtml
        np.write_text(
            np.read_text(encoding="utf-8").format(
                language_code=lang_code,
                nav_title=nav_title,
                foreword_title=foreword_title,
                cover_title=cover_title,
                nav_li_tag_list="\n".join(nav_li_tag_list),
            ),
            encoding="utf-8",
        )
        # write to content.opf
        op.write_text(
            op.read_text(encoding="utf-8").format(
                novel_title=novel_title,
                author_name=fw_lines[14][5:-4],
                language_code=lang_code,
                publisher_name=publisher_name,
                date_created=datetime.now().strftime("%Y-%m-%d"),
                date_modified=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                novel_uuid=novel_uuid,
                ext=ext,
                opf_item_tag_list="\n    ".join(opf_item_tag_list),
                opf_itemref_tag_list="\n    ".join(opf_itemref_tag_list),
            ),
            encoding="utf-8",
        )
        # write to toc.ncx
        ncxp.write_text(
            ncxp.read_text(encoding="utf-8").format(
                novel_uuid=novel_uuid,
                novel_title=novel_title,
                foreword_title=foreword_title,
                navpoint_tag_list="\n".join(navpoint_tag_list),
            ),
            encoding="utf-8",
        )
        # zip files to epub
        with ZipFile(
            self.rp / f"{novel_title}.epub",
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
        copy(str(files(data).joinpath("template/mimetype")), self.epub)
        _logger.info("Done making epub. View result at: %s", self.rp.resolve())


class EpubMakerError(Exception):
    """Handle EpubMaker exception."""


def copytree_hm(src: Path, dst: Path):
    """Copy files in src directory to dst directory recursively.

    Parameters
    ----------
    src : Path
        Path of src directory.
    dst : Path
        Path of dst directory.
    """
    dst.mkdir(exist_ok=True, parents=True)
    for item in src.iterdir():
        if item.is_file():
            copy(item, dst)
        if item.is_dir():
            ndst = dst / item.name
            ndst.mkdir(exist_ok=True, parents=True)
            copytree_hm(item, ndst)
