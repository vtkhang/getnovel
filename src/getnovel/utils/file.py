"""Define FileConverter class."""
import html
import logging
from importlib.resources import files
from pathlib import Path

from getnovel import data

TEMPLATE = Path(files(data).joinpath("template/OEBPS/Text"))
CHAPTER = TEMPLATE / "c1.xhtml"
FOREWORD = TEMPLATE / "foreword.xhtml"
PA = ".,:"

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level="INFO",
)
_logger = logging.getLogger(__name__)


class FileHandler:
    """Handle files."""

    def __init__(self: "FileHandler", raw: Path) -> None:
        """Init path of raw directory.

        Parameters
        ----------
        raw : Path
            Path of raw directory.
        """
        self.raw = raw.resolve()
        self.result: Path = None  # Path of result directory
        self.raw_cover = self.raw / "cover.jpg"  # Path of the raw cover
        self.raw_foreword = self.raw / "foreword.txt"  # Path of the raw foreword

    def process(
        self: "FileHandler",
        action: str,
        **options: Path | str | bool | None,
    ) -> None:
        """Post proccess files.

        Parameters
        ----------
        action : str
                action of the process.
        options:
            result : Path | str | None
                Path of result directory.
        """
        result = options.get("result")
        if not result:
            result = self.raw.parent / action
        self.result = Path(result).resolve()
        self.result.mkdir(parents=True, exist_ok=True)
        if self.raw_cover.exists():
            dest_cover = self.result / self.raw_cover.name
            dest_cover.write_bytes(self.raw_cover.read_bytes())


class FileCleaner(FileHandler):
    """Clean files."""

    def process(self: "FileCleaner", **options: Path | bool | None) -> None:
        """Clean raw files in raw directory.

        Parameters
        ----------
        options:
            result : Path | str | None
                Path of result directory.
            dedup : bool
                If specified, deduplicate chapter title.
        """
        super().process("cleaned", **options)
        self.__clean_foreword()
        self.__clean_chapter(dedup=options.get("dedup"))
        _logger.info("Done cleaning. View result at: %s", self.result)

    def __clean_foreword(self: "FileCleaner") -> None:
        if self.raw_foreword.exists():
            lines = self.raw_foreword.read_text(encoding="utf-8").splitlines()
            foreword = lines[:4]
            foreword.extend(fix_bad_newline(lines[4:]))
            (self.result / "foreword.txt").write_text(
                "\n".join(foreword),
                encoding="utf-8",
            )

    def __clean_chapter(self: "FileCleaner", *, dedup: bool) -> None:
        for chapter_path in self.raw.glob("*[0-9].txt"):
            lines = chapter_path.read_text(encoding="utf-8").splitlines()
            chapter = lines[:1]
            content = lines[1:]
            if dedup:
                content = dedup_title(content)
            chapter.extend(fix_bad_newline(content))
            (self.result / chapter_path.name).write_text(
                "\n".join(chapter),
                encoding="utf-8",
            )


class XhtmlFileConverter(FileHandler):
    """Convert files."""

    def process(
        self: "XhtmlFileConverter",
        **options: Path | bool | str | None,
    ) -> None:
        """Convert files in raw directory to XHTML.

        Parameters
        ----------
        options:
            result : Path | str | None
                Path of result directory.
            dedup : bool
                If specified, deduplicate chapter title.
            lang_code : str
                Language code of the novel.
        """
        super().process("converted", **options)
        self.__convert_foreword(options.get("lang_code"))
        self.__convert_chapter(dedup=options.get("dedup"))
        _logger.info("Done converting. View result at: %s", self.result)

    def __convert_foreword(self: "XhtmlFileConverter", lang_code: str) -> None:
        if self.raw_foreword.exists():
            lines = self.raw_foreword.read_text(encoding="utf-8").splitlines()
            foreword = lines[:4]
            foreword.extend(fix_bad_newline(lines[4:]))
            foreword = [html.escape(line) for line in foreword]
            p_tags = [f"<p>{line}</p>" for line in foreword[4:]]
            foreword_title = "Lời tựa" if lang_code == "vi" else "内容简介"
            (self.result / "foreword.xhtml").write_text(
                FOREWORD.read_text(encoding="utf-8").format(
                    foreword_title=foreword_title,
                    novel_title=foreword[0],
                    author_name=foreword[1],
                    types=foreword[2],
                    url=foreword[3],
                    foreword_p_tag_list="\n\n  ".join(p_tags),
                ),
                encoding="utf-8",
            )

    def __convert_chapter(self: "XhtmlFileConverter", *, dedup: bool) -> None:
        for chapter_path in self.raw.glob("*[0-9].txt"):
            lines = chapter_path.read_text(encoding="utf-8").splitlines()
            chapter = lines[:1]
            content = lines[1:]
            if dedup:
                content = dedup_title(content)
            chapter.extend(fix_bad_newline(content))
            chapter = [html.escape(line) for line in chapter]
            p_tags = [f"<p>{line}</p>" for line in chapter[1:]]
            (self.result / chapter_path.with_suffix(".xhtml").name).write_text(
                CHAPTER.read_text(encoding="utf-8").format(
                    chapter_title=chapter[0],
                    chapter_p_tag_list="\n\n  ".join(p_tags),
                ),
                encoding="utf-8",
            )


def fix_bad_newline(lines: list[str]) -> list[str]:
    """Tidy the result.

    Filtered blank lines. Concatenate lines that
    likely to be in the same setence.

    Examples
    --------
    >>> fix_bad_newline(["A and", "b"])
    >>> ["A and b"]

    Parameters
    ----------
    lines : list[str]
        Input lines.

    Returns
    -------
    list[str]
        Fixed lines.
    """
    lines = lines.copy()
    s_lines: list[str] = [line.strip() for line in lines if line.strip()]
    result: list[str] = []
    result.append(s_lines[0])
    for line in s_lines[1:]:
        last = result[-1][-1]
        first = line[0]
        if last == "," or last.islower() or first.islower():
            result[-1] += " " + line
        elif first in PA:
            result += line
        else:
            result.append(line)
    return result


def dedup_title(
    lines: list[str],
    identities: set = ("Chương", "章"),
    max_length: int = 100,
) -> list[str]:
    """Deduplicate chapter title.

    Parameters
    ----------
    lines : list[str]
        Input lines.
    identities : set, optional
        Identify key, by default ("Chương", "章")
    max_length : int, optional
        Max length of chapter title, by default 100

    Returns
    -------
    list[str]
        Deduplicated chapter title.
    """
    lines = lines.copy()
    for index, line in enumerate(lines):
        for k in identities:
            if k in line and len(line) < max_length:
                del lines[index]
    return lines
