"""GETNOVEL.

GETNOVEL uses the Scrapy framework to download novel from a website
and convert all chapters to XHTML, TXT, or to make EPUB.
"""

import argparse
import sys
import traceback
from pathlib import Path

from getnovel.utils import arguments

__version__ = "1.5.0"


def main(argv) -> int:
    """Main program.

    Parameters
    ----------
    argv : Any
        Command-line arguments, such as sys.argv (including the program name in argv[0])

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


def _build_parser():
    """Constructs the parser for the command line arguments.

    Usage
    -----
        getnovel crawl [-h] [--start] [--stop] [--rm] [--result] [--clean] url

        getnovel convert [-h] [--lang] [--dedup] [--rm] [--result] raw

        getnovel dedup [-h] [--result] raw

        getnovel epub from_url [-h] [--dedup] [--start] [--stop] url

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
        "--start",
        type=int,
        default=1,
        help="start crawling from this chapter (default:  %(default)s)",
        metavar="",
    )
    crawl.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="stop crawling after this chapter,"
        " input -1 to get all chapters (default:  %(default)s)",
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
        default=str(Path.cwd() / "raw"),
        help="path of the result directory (default: current working directory)",
        metavar="",
    )
    crawl.add_argument(
        "--clean",
        action="store_true",
        help="if specified, clean result files after crawling (default:  %(default)s)",
    )
    crawl.add_argument(
        "url",
        type=str,
        help="url of the novel information page",
    )
    crawl.set_defaults(func=arguments.crawl_func)
    # convert parser
    convert = subparsers.add_parser("convert", help="convert chapters to xhtml")
    convert.add_argument(
        "--lang",
        default="vi",
        help="language code of the novel (default:  %(default)s)",
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
        default=str(Path.cwd() / "converted"),
        help="path of result directory (default: current working directory)",
        metavar="",
    )
    convert.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
        metavar="",
    )
    convert.set_defaults(func=arguments.convert_func)
    # deduplicate
    dedup = subparsers.add_parser("dedup", help="deduplicate chapter title")
    dedup.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd() / "deduplicated"),
        help="path of result directory (default: current working directory)",
        metavar="",
    )
    dedup.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
    )
    dedup.set_defaults(func=arguments.dedup_func)
    # epub parser
    epub = subparsers.add_parser("epub", help="make epub")
    subparsers_epub = epub.add_subparsers(title="modes", help="supported modes")
    # epub from_url parser
    from_url = subparsers_epub.add_parser("from_url", help="make epub from web site")
    from_url.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd().resolve()),
        help="path of result directory (default: current working directory)",
        metavar="",
    )
    from_url.add_argument(
        "url",
        type=str,
        help="url of the novel information page",
    )
    from_url.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default:  %(default)s)",
    )
    from_url.add_argument(
        "--start",
        type=int,
        default=1,
        help="start crawling from this chapter (default:  %(default)s)",
        metavar="",
    )
    from_url.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="Stop crawling after this chapter,"
        " input -1 to get all chapters (default:  %(default)s)",
        metavar="",
    )
    from_url.set_defaults(func=arguments.epub_from_url_func)
    # epub from_raw parser
    from_raw = subparsers_epub.add_parser(
        "from_raw", help="make epub from raw directory"
    )
    from_raw.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd().resolve()),
        help="path of result directory (default: current working directory)",
        metavar="",
    )
    from_raw.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
    )
    from_raw.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default:  %(default)s)",
    )
    from_raw.add_argument(
        "--lang",
        default="vi",
        help="language code of the novel (default:  %(default)s)",
        metavar="",
    )

    from_raw.set_defaults(func=arguments.epub_from_raw_func)
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
