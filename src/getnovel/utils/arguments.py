"""Process arguments."""

from pathlib import Path

from getnovel.utils.crawler import NovelCrawler
from getnovel.utils.epub import EpubMaker
from getnovel.utils.file import FileCleaner, XhtmlFileConverter


def crawl_func(args: dict) -> None:
    """Run crawling process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        start=int(args.start),
        stop=int(args.stop),
        result=args.result,
    )
    if args.clean:
        cvt = FileCleaner(raw=p.result)
        cvt.process(result=p.result.parent / "cleaned")


def convert_func(args: dict) -> None:
    """Convert process."""
    cvt = XhtmlFileConverter(raw=Path(args.raw))
    cvt.process(result=args.result, lang_code=args.lang)


def dedup_func(args: dict) -> None:
    """Deduplicate chapter title."""
    raw = Path(args.raw)
    result = raw.parent / "dedup"
    if args.result:
        result = Path(args.result)
    cvt = FileCleaner(raw=raw)
    cvt.process(result=result, dedup=True)


def epub_from_raw_func(args: dict) -> None:
    """Make epub from raw process."""
    maker = EpubMaker(raw=Path(args.raw), lang_code=args.lang)
    maker.process(result=args.result, dedup=args.dedup)


def epub_from_url_func(args: dict) -> None:
    """Make epub from url process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        start=int(args.start),
        stop=int(args.stop),
        result=args.result,
    )
    result = Path(args.result) if args.result else Path.cwd()
    maker = EpubMaker(raw=p.result, lang_code=p.spider.lang_code)
    maker.process(result=result, dedup=args.dedup)
