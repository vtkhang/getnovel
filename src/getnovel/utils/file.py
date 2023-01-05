"""Define FileConverter class.

Limitations
-----------
    1. Can only work with exact structure and file name: cover.jpg, foreword.txt, 1.txt,...
    2. Can only work with exact file structure:
        - foreword: line 1 is title, line 2 is author, line 3 is types,
        line 4 is url, rest are foreword.
        - chapter: line 1 is chapter title, rest are content.
"""
import sys
import html
import logging
from pathlib import Path
from shutil import rmtree

if sys.version_info >= (3, 8):
    from importlib.resources import files
else:
    from importlib_resources import files

from getnovel import data
from getnovel.utils.typehint import PathStr, DictPath, ListStr

_logger = logging.getLogger(__name__)


class FileConverter:
    """This class define clean method and convert to xhtml method."""

    def __init__(self, raw: PathStr, result: PathStr = None):
        """Init path of raw directory and result directory.

        Parameters
        ----------
        raw : PathStr
            Path of raw directory.
        result : PathStr, optional
            Path of result directory, by default None.

        Raises
        ------
        FileConverterError
            Raw directory not found.
        FileConverterError
            Raw directory is empty.
        """
        self.x = Path(raw)
        if not self.x.exists():
            raise FileConverterError(f"Raw directory not found: {self.x}")
        if not any(self.x.iterdir()):
            raise FileConverterError("Raw directory is empty.")
        if result is None:
            self.y = self.x.parent / "result_dir"
        else:
            self.y = Path(result)
        if not self.y.exists():
            self.y.mkdir(parents=True)
            _logger.info(
                f"Result directory not found, auto created at: {self.y.resolve()}"
            )
        self.txt: DictPath = {}  # use to track txt files in result directory
        self.xhtml: DictPath = {}  # use to track xhtml files in result directory

    def clean(self, dedup: bool, rm_result: bool) -> int:
        """Clean raw files in raw directory.

        Parameters
        ----------
        dedup : bool
            If specified, deduplicate chapter title.
        rm_result : bool
            If specified, remove all old files in result directory.

        Returns
        -------
        int
            Value -1 if raw directory empty
        """
        # remove old files in result directory
        if rm_result is True:
            _logger.info(f"Remove existing files in: {self.y.resolve()}")
            self._rm_result()
        # copy cover image to result directory
        cop = self.x / "cover.jpg"
        if cop.exists():
            copn = self.y / cop.name
            copn.write_bytes(cop.read_bytes())
            self.txt[-1] = copn
        # clean foreword.txt
        fwp = self.x / "foreword.txt"
        if fwp.exists():
            fwpn = self.y / fwp.name
            process(fwp, "info", fwpn, "clean")
            self.txt[0] = fwpn
        # clean chapter.txt
        f_list = [item for item in self.x.glob("*[0-9].txt")]
        for cp in f_list:
            cpn = self.y / cp.name
            process(cp, "chapter", cpn, "clean", dedup=dedup)
            self.txt[int(cp.stem)] = cpn
        _logger.info(f"Done cleaning. View result at: {self.y.resolve()}")

    def convert_to_xhtml(self, dedup: bool, rm_result: bool, lang_code: str) -> int:
        """Clean files and convert to XHTML.

        Parameters
        ----------
        dedup : bool
            If specified, deduplicate chapter title.
        rm_result : bool
            If specified, remove all old files in result directory.
        lang_code : str
            Language code of the novel.

        Returns
        -------
        int
            Value -1 if raw directory empty

        Raises
        ------
        FileConverterError
            Chapter template not found.
        FileConverterError
            Foreword template not found.
        """
        # Check if default template is exist, if not throw exception
        # template of chapter
        tp = files(data).joinpath(r"template/OEBPS/Text")
        ctp = tp / "c1.xhtml"
        if ctp.exists() is False or ctp.is_dir():
            raise FileConverterError(f"Chapter template not found: {ctp}")
        # template of foreword
        fwtp = tp / "foreword.xhtml"
        if fwtp.exists() is False or fwtp.is_dir():
            raise FileConverterError(f"Foreword template not found: {ctp}")
        # remove old files in result directory
        if rm_result is True:
            _logger.info(f"Remove existing files in: {self.y.resolve()}")
            self._rm_result()
        # copy cover image to result dir
        cop = self.x / "cover.jpg"
        if cop.exists():
            copn = self.y / cop.name
            copn.write_bytes(cop.read_bytes())
            self.xhtml[-1] = copn
        # convert foreword.txt
        fwp = self.x / "foreword.txt"
        if fwp.exists():
            fwpn = self.y / (fwp.with_suffix(".xhtml")).name
            process(fwp, "info", fwpn, "convert", fwtp, lang_code)
            self.xhtml[0] = fwpn
        # clean chapter.txt
        f_list = [item for item in self.x.glob("*[0-9].txt")]
        for cp in f_list:
            cpn = self.y / f"c{cp.stem}.xhtml"
            process(cp, "chapter", cpn, "convert", ctp, dedup=dedup)
            self.xhtml[int(cp.stem)] = cpn
        _logger.info("Done converting. View result at: %s", self.y.resolve())

    def _rm_result(self) -> int:
        """Remove all files in result directory.

        Returns:
            int: -1 if result directory is raw directory
        """
        if self.x == self.y:
            # TODO: create temporary directory to store old files to process.
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


def fix_bad_newline(lines: ListStr):
    """Filtered blank lines. Concatenate lines that
    likely to be in the same setence.

    Examples
    --------
    >>> fix_bad_newline(("A and", "b"))
    >>> ("A and b")

    Parameters
    ----------
    lines : List
        Input lines.

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
    return result


def dedup_title(
    content_lines: ListStr,
    chapter_path: Path,
    identities: ListStr = ["Chương", "章"],
    max_length: int = 100,
) -> ListStr:
    """Deduplicate chapter title.

    Parameters
    ----------
    content_lines : ListStr
        Chapter content splitted into lines.
    chapter_path: Path
        Use chapter path to display debug messages.
    identities : ListStr
        Identify key, by default ["Chương", "章"]
    max_length : int, optional
        Max length of chapter title, by default 100

    Returns
    -------
    ListStr
        Deduplicated chapter title.
    """
    index = 0
    for line in content_lines:
        s = len(identities)
        for k in identities:
            if k in line and len(line) < max_length:
                _logger.debug(msg=f"Removed: {content_lines[index]}")
                index += 1
                break
            else:
                s -= 1
        if s == 0:
            break
    if index != 0:
        _logger.debug(msg=f"Path: {chapter_path}")
    return content_lines[index:]


def process(
    ip: Path,
    t: str,
    sp: Path,
    m: str,
    tp: Path = None,
    lang: str = "vi",
    dedup: bool = False,
):
    """Clean file or convert file to xhtml.

    Parameters
    ----------
    ip : Path
        Path of input file.
    t : str
        Type of the file (info or chapter).
    sp : Path
        Path of output file.
    m : str
        Mode (clean or xhtml).
    tp : Path, optional
        Path of template files to convert to xhtml, by default None
    lang : str, optional
        Language code for info xhtml page, by default "vi"
    dedup : bool, optional
        If specified, deduplicate chapter title, by default False
    """
    lines = ip.read_text(encoding="utf-8").splitlines()
    index = 0
    if t == "info":
        index = 4
    elif t == "chapter":
        index = 1
        if dedup:
            lines[index:] = dedup_title(lines[index:], ip)
    r = lines[:index]
    r.extend(fix_bad_newline(lines[index:]))
    if m == "clean":
        sp.write_text("\n".join(r), encoding="utf-8")
    elif m == "convert":
        r = [html.escape(line) for line in r]
        p_tags = [f"<p>{line}</p>" for line in r[index:]]
        if t == "info":
            foreword_title = "Lời tựa"
            if lang == "zh":
                foreword_title = "内容简介"
            sp.write_text(
                tp.read_text(encoding="utf-8").format(
                    foreword_title=foreword_title,
                    novel_title=r[0],
                    author_name=r[1],
                    types=r[2],
                    url=r[3],
                    foreword_p_tag_list="\n\n  ".join(p_tags),
                ),
                encoding="utf-8",
            )
        elif t == "chapter":
            sp.write_text(
                tp.read_text(encoding="utf-8").format(
                    chapter_title=r[0],
                    chapter_p_tag_list="\n\n  ".join(p_tags),
                ),
                encoding="utf-8",
            )
