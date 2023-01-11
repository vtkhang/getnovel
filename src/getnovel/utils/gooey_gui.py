"""Build GUI for GETNOVEL."""

from pathlib import Path

from gooey import Gooey, GooeyParser
from getnovel.utils import arguments


@Gooey(target="getnovel_gui", default_size=(1000, 700), program_name="Get Novel")
def main_gui():
    """Main GUI program.

    Returns
    -------
    int
        Zero on successful program termination, non-zero otherwise.
    """
    parser = GooeyParser(prog="getnovel", allow_abbrev=False, description="Get novel from websites")
    subparsers = parser.add_subparsers(title="modes", help="supported modes")
    # crawl parser
    crawl = subparsers.add_parser("crawl", help="get novel content")
    crawl.add_argument(
        "--start",
        type=int,
        default=1,
        help="start crawling from this chapter (default: 1)",
        metavar="",
    )
    crawl.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="stop crawling after this chapter,"
             " input -1 to get all chapters (default: -1)",
        metavar="",
    )
    crawl.add_argument(
        "--rm",
        action="store_true",
        help="if specified, remove old files in the result directory (default: False)",
    )
    crawl.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd() / "raw"),
        help="path of the result directory (default: None)",
        metavar="",
        widget="DirChooser",
    )
    crawl.add_argument(
        "--clean",
        action="store_true",
        help="if specified, clean result files after crawling (default: False)",
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
        help="language code of the novel (default: vi)",
        metavar="",
    )
    convert.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default: False)",
    )
    convert.add_argument(
        "--rm",
        action="store_true",
        help="if specified, remove old files in result directory (default: False)",
    )
    convert.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd() / "converted"),
        help="path of result directory",
        metavar="",
        widget="DirChooser",
    )
    convert.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
        metavar="",
        widget="DirChooser",
    )
    convert.set_defaults(func=arguments.convert_func)
    # deduplicate
    dedup = subparsers.add_parser("dedup", help="deduplicate chapter title")
    dedup.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd() / "deduplicated"),
        help="path of result directory",
        metavar="",
        widget="DirChooser",
    )
    dedup.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
        widget="DirChooser",
    )
    dedup.set_defaults(func=arguments.dedup_func)
    # epub from url parser
    epub_from_url = subparsers.add_parser("epub_from_url", help="make epub from web site")
    epub_from_url.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd().resolve()),
        help="path of result directory (default: current working directory)",
        metavar="",
        widget="DirChooser",
    )
    epub_from_url.add_argument(
        "url",
        type=str,
        help="url of the novel information page",
    )
    epub_from_url.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default: False)",
    )
    epub_from_url.add_argument(
        "--start",
        type=int,
        default=1,
        help="start crawling from this chapter (default: 1)",
        metavar="",
    )
    epub_from_url.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="stop crawling after this chapter,"
             " input -1 to get all chapters (default: -1)",
        metavar="",
    )
    epub_from_url.set_defaults(func=arguments.epub_from_url_func)
    # epub from raw parser
    epub_from_raw = subparsers.add_parser(
        "epub_from_raw", help="make epub from raw directory"
    )
    epub_from_raw.add_argument(
        "--result",
        type=str,
        default=str(Path.cwd().resolve()),
        help="path of result directory (default: current working directory)",
        metavar="",
        widget="DirChooser",
    )
    epub_from_raw.add_argument(
        "raw",
        type=str,
        help="path of raw directory",
        widget="DirChooser",
    )
    epub_from_raw.add_argument(
        "--dedup",
        action="store_true",
        help="if specified, deduplicate chapter title (default: False)",
    )
    epub_from_raw.add_argument(
        "--lang",
        default="vi",
        help="language code of the novel (default: vi)",
        metavar="",
    )
    epub_from_raw.set_defaults(func=arguments.epub_from_raw_func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_gui()
