"""Store the settings of spider for utils crawler."""

import json
import time
import pprint
from pathlib import Path


def get_settings(
    log_level: str,
    result: Path = None,
):
    """Generate project settings.

    Parameters
    ----------
    result : Path, optional
        Path of result directory, by default None
    log_level : str, optional
        Log level of logging, by default "INFO"
    lp : Path, optional
        Path of directory that stores logs, by default None

    Returns
    -------
    dict
        Settings.
    """
    hp = Path.home()
    # Default image path for imagepipeline
    imgp = hp / "GetNovel" / "images"
    imgp.mkdir(parents=True, exist_ok=True)
    # Result directory
    if result is None:
        result = hp / "GetNovel" / "crawled"
    result = Path(result)
    result.mkdir(parents=True, exist_ok=True)
    # Log
    lp = hp / "GetNovel" / "logs"
    lp.mkdir(parents=True, exist_ok=True)
    lnp = lp / f'{time.strftime("%Y_%m_%d-%H_%M_%S")}.log'
    print(f"> Please view log file at: {str(lnp)}")
    return {
        "BOT_NAME": "GetNovel",
        "ROBOTSTXT_OBEY": True,
        "SPIDER_MODULES": ["getnovel.app.spiders"],
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54",
        # ITEM PIPELINES
        "ITEM_PIPELINES": {
            "getnovel.app.pipelines.AppPipeline": 300,
            "getnovel.app.pipelines.CoverImagesPipeline": 200,
        },
        "IMAGES_STORE": str(imgp),
        # DOWNLOADER_MIDDLEWARES
        "DOWNLOADER_MIDDLEWARES": {
            "getnovel.app.middlewares.AppDownloaderMiddleware": 500,
        },
        # LOG SETTINGS
        "LOG_FORMAT": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        "LOG_SHORT_NAMES": True,
        "LOG_FILE": str(lnp),
        "LOG_FILE_APPEND": False,
        "LOG_LEVEL": log_level,
        # AUTOTHROTTLE SETTINGS
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 6,
        "DOWNLOAD_DELAY": 3,
        "AUTOTHROTTLE_MAX_DELAY": 60,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,
        # COOKIE
        "COOKIES_DEBUG": True,
        # SAVE PATH
        "RESULT": str(result),
    }


def mk_settings(sp: Path, sc: dict):
    """Create setting file for scrapy project from dict."""
    r = []
    r.append("# flake8: noqa")
    for k in sc:
        t = ""
        if type(sc[k]) == str:
            t = f'r"{str(sc[k])}"'
        elif type(sc[k]) == dict:
            t = json.dumps(sc[k], indent=4)
        elif type(sc[k]) == list:
            t = f"{pprint.pformat(sc[k], indent=4)}"
        else:
            t = str(sc[k])
        r.append(f"{str(k)} = {t}")
    r.append("")
    sp.absolute().write_text(encoding="utf-8", data="\n".join(r))


if __name__ == "__main__":
    """Workplace."""
    pass
