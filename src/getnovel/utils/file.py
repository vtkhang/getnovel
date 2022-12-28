"""Define FileConverter class."""
import html
import logging
from pathlib import Path
from shutil import rmtree, copy

try:
    from importlib_resources import files
except ImportError:
    from importlib.resources import files

from getnovel import data
from getnovel.utils.typehint import PathStr, DictPath, ListStr

_logger = logging.getLogger(__name__)


class FileConverter:
    """This class define clean method and convert to xhtml method."""

    def __init__(self, raw_dir_path: PathStr, result_dir_path: PathStr = None) -> None:
        """Init path of raw directory and result directory.

        Args:
            raw_dir_path: path of raw directory
            result_dir_path: path of result directory

        Returns:
            None
        """
        self.x = Path(raw_dir_path)
        if not self.x.exists():
            raise FileConverterError(f"Raw directory not found: {self.x}")
        if not any(self.x.iterdir()):
            raise FileConverterError("Raw directory is empty.")
        if result_dir_path is None:
            self.y = self.x.parent / "result_dir"
        else:
            self.y = Path(result_dir_path)
        if not self.y.exists():
            self.y.mkdir(parents=True)
            _logger.info(
                "Result directory not found, auto created at: %s", self.y.resolve()
            )
        self.txt: DictPath = {}  # use to track txt files in result directory
        self.xhtml: DictPath = {}  # use to track xhtml files in result directory

    def clean(self, dedup: bool, rm_result: bool) -> int:
        """Clean all raw files in raw directory.

        Args:
            dedup: if specified, remove duplicate chapter title
            rm_result: if specified, remove all old files in result directory

        Returns:
            int: -1 if raw directory empty
        """
        if rm_result is True:
            _logger.info("Remove existing files in: %s", self.y.resolve())
            self._rm_result()
        # copy cover image to result directory
        cover_path = self.x / "cover.jpg"
        tmp = self.y / cover_path.name
        if tmp != cover_path:
            copy(cover_path, tmp)
        self.txt[-1] = tmp
        # clean foreword.txt
        fw_path = self.x / "foreword.txt"
        fw_lines = fw_path.read_text(encoding="utf-8").splitlines()
        r = fw_lines[:4]
        r.extend(fix_bad_newline(fw_lines[4:]))
        tmp = self.y / fw_path.name
        tmp.write_text("\n".join(r), encoding="utf-8")
        self.txt[0] = tmp
        # clean chapter.txt
        f_list = [item for item in self.x.glob("*[0-9].txt")]
        for chapter in f_list:
            r = []
            c_lines = chapter.read_text(encoding="utf-8").splitlines()
            r.append(c_lines.pop(0))
            if dedup is True:
                c_lines = dedup_title_plus(c_lines, chapter)
            if len(c_lines) == 0:
                _logger.error(
                    f"The structure of chapter {chapter.stem} is wrong!"
                    f"\nPath: {chapter}"
                )
                continue
            r.extend(fix_bad_newline(c_lines))
            tmp = self.y / chapter.name
            tmp.write_text("\n".join(r), encoding="utf-8")
            self.txt[int(chapter.stem)] = tmp
        _logger.info("Done cleaning. View result at: %s", self.y.resolve())

    def convert_to_xhtml(self, dedup: bool, rm_result: bool, lang_code: str) -> int:
        """Clean files and convert to XHTML.

        Args:
            dedup: if specified, remove duplicate chapter title
            rm_result: if specified, remove all old files in result directory
            lang_code: language code of the novel

        Returns:
            int: -1 if raw directory empty
        """
        # Check if default template is exist, if not throw exception
        # template of chapter
        txtp = files(data).joinpath(r"template/OEBPS/Text")
        ctp = txtp / "c1.xhtml"
        if ctp.exists() is False or ctp.is_dir():
            raise FileConverterError(f"Chapter template not found: {ctp}")
        # template of foreword
        fwtp = txtp / "foreword.xhtml"
        if fwtp.exists() is False or fwtp.is_dir():
            raise FileConverterError(f"Foreword template not found: {ctp}")
        # remove old files in result directory
        if rm_result is True:
            _logger.info("Remove existing files in: %s", self.y.resolve())
            self._rm_result()
        # copy cover image to result dir
        cover_path = self.x / "cover.jpg"
        tmp = self.y / cover_path.name
        if tmp != cover_path:
            copy(cover_path, tmp)
        self.xhtml[-1] = tmp
        # clean foreword.txt
        fwp = self.x / "foreword.txt"
        fw_lines = fwp.read_text(encoding="utf-8").splitlines()
        foreword_p_tag_list = [
            f"<p>{line}</p>" for line in fix_bad_newline(fw_lines[4:], escape=True)
        ]
        foreword_title = "Lời tựa"
        if lang_code == "zh":
            foreword_title = "内容简介"
        tmp = self.y / f"{fwp.stem}.xhtml"
        tmp.write_text(
            fwtp.read_text(encoding="utf-8").format(
                foreword_title=foreword_title,
                novel_title=html.escape(fw_lines[0]),
                author_name=html.escape(fw_lines[1]),
                types=html.escape(fw_lines[2]),
                url=fw_lines[3],
                foreword_p_tag_list="\n\n  ".join(foreword_p_tag_list),
            ),
            encoding="utf-8",
        )
        self.xhtml[0] = tmp
        # clean chapter.txt
        f_list = [item for item in self.x.glob("*[0-9].txt")]
        for chapter in f_list:
            c_lines = chapter.read_text(encoding="utf-8").splitlines()
            title = c_lines.pop(0)
            if dedup is True:
                c_lines = dedup_title_plus(c_lines, chapter)
            if len(c_lines) == 0:
                _logger.error(
                    f"The structure of chapter {chapter.stem} is wrong!"
                    f"\nPath: {chapter}"
                )
                continue
            tmp = self.y / f"c{chapter.stem}.xhtml"
            chapter_p_tag_list = [
                f"<p>{line}</p>"
                for line in fix_bad_newline(tuple(c_lines), escape=True)
            ]
            tmp.write_text(
                ctp.read_text(encoding="utf-8").format(
                    chapter_title=title,
                    chapter_p_tag_list="\n\n  ".join(chapter_p_tag_list),
                ),
                encoding="utf-8",
            )
            self.xhtml[int(chapter.stem)] = tmp
        _logger.info("Done converting. View result at: %s", self.y.resolve())

    def _rm_result(self) -> int:
        """Remove all files in result directory.

        Returns:
            int: -1 if result directory is raw directory
        """
        if self.x == self.y:
            return -1
        rmtree(self.y)
        self.y.mkdir()
        self.txt = {}
        self.xhtml = {}

    def _update_file_list(self, ext: str) -> None:
        """Remove all files not existing.

        Returns:
            None
        """
        # https://www.geeksforgeeks.org/python-delete-items-from-dictionary-while-iterating/
        t = {}
        if ext == "txt":
            t = self.txt
        elif ext == "xhtml":
            t = self.xhtml
        for key in list(t):
            if not t[key].exists():
                del t[key]

    def get_result_dir(self) -> Path:
        """Return path of result directory.

        Returns:
            Path: path of result directory
        """
        return self.y

    def get_file_list(self, ext: str) -> tuple:
        """Return result file paths list.

        Args:
            ext: extension of files [txt, xhtml]

        Returns:
            tuple: file paths list
        """
        t = {}
        if ext == "txt":
            self._update_file_list(ext="txt")
            t = self.txt
        elif ext == "xhtml":
            self._update_file_list(ext="xhtml")
            t = self.xhtml
        return tuple([value for key, value in sorted(t.items())])


class FileConverterError(Exception):
    """File converter exception"""

    pass


def fix_bad_newline(lines: ListStr, escape: bool = False):
    """Filtered blank lines. Concatenate lines that
    likely to be in the same setence. Escape all lines if `escape` is True.

    Examples
    --------
    >>> fix_bad_newline(("A and", "b"))
    >>> ("A and b")

    Parameters
    ----------
    lines : List
        Input lines.
    escape : bool, optional
        If True escape lines for html, by default False

    Returns
    -------
    List
        Fixed lines.
    """
    flines = []
    result = []
    pa = ".,:"
    for line in lines:
        t = line.strip()
        if t:
            flines.append(t)
    if not flines:
        _logger.error("Input data does not contain any valid line.")
        return None
    result.append(flines[0])
    if len(flines) == 1:
        return result
    for index in range(1, len(flines)):
        last = result[-1][-1]
        first = flines[index][0]
        if (
            (last == ",")
            or (first.islower())
            or (last.islower())
            or (last == '"' and first.islower())
            or (first == '"' and last.islower())
        ):
            result[-1] = result[-1] + " " + flines[index]
        elif first in pa:
            result[-1] = result[-1] + flines[index]
        else:
            result.append(flines[index])
    if escape:
        return [html.escape(line) for line in result]
    return result


def dedup_title_plus(
    chapter_lines: ListStr,
    chapter_path: Path,
    identities: ListStr = ["Chương", "章"],
    max_length: int = 100,
) -> ListStr:
    """Deduplicate chapter title.

    Parameters
    ----------
    chapter_lines : ListStr
        Chapter content splitted into lines.
    identities : ListStr, optional
        Identify key, by default ["Chương", "章"]
    max_length : int, optional
        Max length of chapter title, by default 100

    Returns
    -------
    ListStr
        Deduplicated chapter title.
    """
    index = 0
    for line in chapter_lines:
        s = len(identities)
        for k in identities:
            if k in line and len(line) < max_length:
                _logger.debug(msg=f"Removed: {chapter_lines[index]}")
                index += 1
                break
            else:
                s -= 1
        if s == 0:
            break
    if index != 0:
        _logger.debug(mse=f"Path: {chapter_path}")
    return chapter_lines[index:]
