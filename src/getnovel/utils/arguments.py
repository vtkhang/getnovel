"""Process arguments."""

from pathlib import Path
from getnovel.utils.crawler import NovelCrawler
from getnovel.utils.epub import EpubMaker
from getnovel.utils.file import FileConverter


def crawl_func(args):
    """Run crawling process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        rm=args.rm,
        start=args.start,
        stop=args.stop,
        clean=args.clean,
        result=Path(args.result),
        custom_settings=args.settings,
    )


def convert_func(args):
    """Convert process."""
    c = FileConverter(
        raw=Path(args.raw),
        result=Path(args.result),
    )
    c.convert_to_xhtml(
        lang_code=args.lang,
        dedup=args.dedup,
        rm=args.rm,
    )


def dedup_func(args):
    """Deduplicate chapter title."""
    c = FileConverter(
        raw=Path(args.raw),
        result=Path(args.result),
    )
    c.clean(dedup=True, rm=False)


def epub_from_url_func(args):
    """Make epub from url process."""
    e = EpubMaker(result=Path(args.result))
    e.from_url(
        url=args.url,
        dedup=args.dedup,
        start=args.start,
        stop=args.stop,
    )


def epub_from_raw_func(args):
    """Make epub from raw process."""
    e = EpubMaker(result=Path(args.result))
    e.from_raw(
        raw=Path(args.raw),
        dedup=args.dedup,
        lang_code=args.lang,
    )
