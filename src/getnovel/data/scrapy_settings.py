"""Store the settings of spider for utils crawler."""

import json
import pprint
import time
from pathlib import Path


def get_settings() -> dict:
    """Generate project settings.

    Returns
    -------
    dict
        Settings.
    """
    hp = Path.home()
    gnp = hp / "GetNovel"
    # Log
    lp = gnp / "logs"
    lp.mkdir(parents=True, exist_ok=True)
    lnp = lp / f'{time.strftime("%Y_%m_%d-%H_%M_%S")}.log'
    return {
        "BOT_NAME": "GetNovel",
        "ROBOTSTXT_OBEY": True,
        "SPIDER_MODULES": ["getnovel.app.spiders"],
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36(KHTML, like Gecko)"
        "Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54",
        # ITEM PIPELINES
        "ITEM_PIPELINES": {
            "getnovel.app.pipelines.AppPipeline": 300,
            "getnovel.app.pipelines.CoverImagesPipeline": 200,
        },
        "IMAGES_STORE": str(gnp / "images"),
        # DOWNLOADER_MIDDLEWARES
        "DOWNLOADER_MIDDLEWARES": {
            "getnovel.app.middlewares.AppDownloaderMiddleware": 500,
        },
        # LOG SETTINGS
        "LOG_FORMAT": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        "LOG_SHORT_NAMES": True,
        "LOG_FILE": str(lnp),
        "LOG_FILE_APPEND": False,
        "LOG_LEVEL": "DEBUG",
        "COOKIES_ENABLED": False,
        # AUTOTHROTTLE SETTINGS
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 6,
        "DOWNLOAD_DELAY": 3,
        "AUTOTHROTTLE_MAX_DELAY": 60,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,
        # CACHE
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": str(gnp / "cache"),
        # SAVE PATH
        "RESULT": str(gnp / "raw"),
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    }


def mk_settings(sp: Path, sc: dict) -> None:
    """Create setting file for scrapy project from dict."""
    r = []
    r.append("# flake8: noqa")
    for k in sc:
        if isinstance(sc[k], str):
            t = f'r"{str(sc[k])}"'
        elif isinstance(sc[k], dict):
            t = json.dumps(sc[k], indent=4)
        elif isinstance(sc[k], list):
            t = f"{pprint.pformat(sc[k], indent=4)}"
        else:
            t = str(sc[k])
        r.append(f"{str(k)} = {t}")
    r.append("")
    sp.absolute().write_text(encoding="utf-8", data="\n".join(r))


if __name__ == "__main__":
    """Workplace."""
