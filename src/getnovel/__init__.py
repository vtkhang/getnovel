"""GETNOVEL.

GETNOVEL uses the Scrapy framework to download novel from a website
and convert all chapters to XHTML, TXT, or to make EPUB.
"""

import sys
import argparse
import traceback
from getnovel.utils.crawler import NovelCrawler
from getnovel.utils.epub import EpubMaker
from getnovel.utils.file import FileConverter

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata
__version__ = metadata.version(__name__)


def main(argv) -> int:
    """Main program.

    Parameters
    ----------
    argv : Any
        command-line arguments, such as sys.argv (including the program name in argv[0])

    Returns
    -------
    int
        Zero on successful program termination, non-zero otherwise.
    """
    parser = _build_parser()
    if len(argv) == 1:
        parser.print_help()
        return 0
    args = parser.parse_args(argv[1:])
    if args.version is True:
        print(f"Getnovel {__version__}")
        return 0
    try:
        args.func(args)
    except AttributeError:
        if argv[1] == "epub":
            print("Missing sub command: from_url, from_raw")
            return 1
        else:
            print(traceback.format_exc())
    return 0


def crawl_func(args):
    """Run crawling process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        rm_raw=args.rm,
        start_index=args.start_index,
        num_chap=args.num_chap,
        clean=args.clean,
        output=args.result,
    )


def convert_func(args):
    """Convert process."""
    c = FileConverter(args.raw, args.result)
    c.convert_to_xhtml(
        lang_code=args.lang,
        dedup=args.dedup,
        rm_result=args.rm,
    )


def dedup_func(args):
    """Deduplicate chapter title."""
    if args.result is None:
        c = FileConverter(args.raw, args.raw)
    else:
        c = FileConverter(args.raw, args.result)
    c.clean(dedup=True, rm_result=False)


def epub_from_url_func(args):
    """Make epub from url process."""
    e = EpubMaker()
    e.from_url(args.url, args.dedup, args.start_index, args.num_chap)


def epub_from_raw_func(args):
    """Make epub from raw process."""
    e = EpubMaker()
    e.from_raw(args.raw, args.dedup, args.lang)


def _build_parser():
    """Constructs the parser for the command line arguments.

    Usage
    -----
        getnovel crawl [-h] [--start_index] [--num_chap] [--rm] [--result] [--clean] url

        getnovel convert [-h] [--lang] [--dedup] [--rm] [--result] raw

        getnovel dedup [-h] [--result] raw

        getnovel epub from_url [-h] [--dedup] [--start_index] [--num_chap] url

        getnovel epub from_raw [-h] [--dedup] [--lang] raw

    Returns
    -------
    int
        An ArgumentParser instance for the CLI.
    """
    # parser
    parser = argparse.ArgumentParser(prog="getnovel", allow_abbrev=False)
    parser.add_argument(
        "-v", "--version", action="store_true", help="show version number and exit"
    )
    subparsers = parser.add_subparsers(title="modes", help="supported modes")
    # crawl parser
    crawl = subparsers.add_parser("crawl", help="get novel content")
    crawl.add_argument(
        "--start_index",
        type=int,
        default=1,
        help="file name will increase from this value (default:  %(default)s)",
        metavar="",
    )
    crawl.add_argument(
        "--num_chap",
        type=int,
        default=-1,
        help="number of chapters to crawl, input -1 to crawl"
        " until the last chapter (default:  %(default)s)",
        metavar="",
    )
    crawl.add_argument(
        "--rm",
        action="store_true",
        help="if specified, remove old files in the result directory (default:  %(default)s)",
    )
    crawl.add_argument(
        "--result",
        type=str,
        default=None,
        help="path of result directory (default:  %(default)s)",
        metavar="",
    )
    crawl.add_argument(
        "--clean",
        action="store_false",
        help="clean all result files after crawling (default:  %(default)s)",
    )
    crawl.add_argument(
        "url",
        type=str,
        help="url to start crawling",
    )
    crawl.set_defaults(func=crawl_func)
    # convert parser
    convert = subparsers.add_parser("convert", help="convert chapters to xhtml")
    convert.add_argument(
        "--lang",
        default="vi",
        help="language code of the novel (default: %(default)s)",
        metavar="",
    )
    convert.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default:  %(default)s)",
    )
    convert.add_argument(
        "--rm",
        action="store_true",
        help="if specified, remove old files in result directory (default:  %(default)s)",
    )
    convert.add_argument(
        "--result",
        type=str,
        default=None,
        help="path of result directory (default:  %(default)s)",
        metavar="",
    )
    convert.add_argument(
        "raw",
        type=str,
        help="path of raw directory (default:  %(default)s)",
        metavar="",
    )
    convert.set_defaults(func=convert_func)
    # deduplicate
    dedup = subparsers.add_parser("dedup", help="deduplicate chapter title")
    dedup.add_argument(
        "--result",
        type=str,
        default=None,
        help="path of result directory (default:  %(default)s)",
        metavar="",
    )
    dedup.add_argument(
        "raw",
        type=str,
        help="path of raw directory (default:  %(default)s)",
    )
    dedup.set_defaults(func=dedup_func)
    # epub parser
    epub = subparsers.add_parser("epub", help="make epub")
    subparsers_epub = epub.add_subparsers(title="modes", help="supported modes")
    # epub from_url parser
    from_url = subparsers_epub.add_parser("from_url", help="make epub from web site")
    from_url.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default:  %(default)s)",
    )
    from_url.add_argument(
        "--start_index",
        type=int,
        default=1,
        help="file name will increase from this value (default:  %(default)s)",
        metavar="",
    )
    from_url.add_argument(
        "--num_chap",
        type=int,
        default=-1,
        help="number of chapters to crawl, input -1 to crawl"
        " until the last chapter (default:  %(default)s)",
        metavar="",
    )
    from_url.add_argument(
        "url",
        type=str,
        help="url to start crawling",
    )
    from_url.set_defaults(func=epub_from_url_func)
    # epub from_raw parser
    from_raw = subparsers_epub.add_parser(
        "from_raw", help="make epub from raw directory"
    )
    from_raw.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default:  %(default)s)",
    )
    from_raw.add_argument(
        "--lang",
        default="vi",
        help="language code of the novel (default: %(default)s)",
        metavar="",
    )
    from_raw.add_argument(
        "raw",
        type=str,
        help="path of raw directory (default:  %(default)s)",
    )
    from_raw.set_defaults(func=epub_from_raw_func)
    return parser


class GetnovelException(BaseException):
    """General exception for getnovel."""

    pass


def run_main():
    """Run main program."""
    try:
        sys.exit(main(sys.argv))
    except GetnovelException as e:
        sys.stderr.write(f"getnovel:{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_main()
