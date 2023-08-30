"""Process arguments."""

from pathlib import Path

from getnovel.utils.crawler import NovelCrawler

# from getnovel.utils.epub import EpubMaker
from getnovel.utils.file import FileCleaner, XhtmlFileConverter


def crawl_func(args: any) -> None:
    """Run crawling process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        start=int(args.start),
        stop=int(args.stop),
        result=args.result,
        rm=args.rm,
    )
    if args.clean:
        cvt = FileCleaner(raw=p.result)
        cvt.process(result=p.result.parent / "cleaned")


def convert_func(args: dict) -> None:
    """Convert process."""
    cvt = XhtmlFileConverter(raw=Path(args.raw))
    cvt.process(result=args.result, lang_code=args.lang, rm=args.rm)


def dedup_func(args: dict) -> None:
    """Deduplicate chapter title."""
    cvt = FileCleaner(raw=Path(args.raw))
    cvt.process(result=args.result, rm=False, dedup=True)


def epub_from_url_func(args: dict) -> None:
    """Make epub from url process."""
    # e = EpubMaker(result=Path(args.result))
    # e.from_url(
    #     url=args.url,
    #     dedup=args.dedup,
    #     start=int(args.start),
    #     stop=int(args.stop),
    # )


def epub_from_raw_func(args: dict) -> None:
    """Make epub from raw process."""
    # e = EpubMaker(result=Path(args.result))
    # e.from_raw(
    #     raw=Path(args.raw),
    #     dedup=args.dedup,
    #     lang_code=args.lang,
    # )
