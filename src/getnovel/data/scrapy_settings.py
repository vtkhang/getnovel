"""Store the settings of spider for utils crawler. """
import json
import pprint
from pathlib import Path


def get_settings():
    """Return the settings of spider.

    Returns
    -------
    dict
        Spider settings.
    """
    return {
        "BOT_NAME": "GetNovel",
        "ROBOTSTXT_OBEY": False,
        "SPIDER_MODULES": ["getnovel.app.spiders"],
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        # ITEM PIPELINES
        "ITEM_PIPELINES": {
            "getnovel.app.pipelines.AppPipeline": 300,
            "getnovel.app.pipelines.CoverImagesPipeline": 200,
        },
        "IMAGES_STORE": f'{Path.home() / "GetNovel" / "images"}',
        # LOG SETTINGS
        "LOG_FORMAT": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        "LOG_SHORT_NAMES": True,
        "LOG_FILE": f'{Path.home() / "GetNovel" / "logs" / "log.txt"}',
        "LOG_FILE_APPEND": False,
        # AUTOTHROTTLE SETTINGS
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 5,
        "DOWNLOAD_DELAY": 2,
        "AUTOTHROTTLE_MAX_DELAY": 60,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,
    }


def mk_settings(sp: Path, sc: dict):
    """Create setting file for scrapy project from dict"""
    r = []
    r.append("# flake8: noqa: E501")
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
    sp.write_text(encoding="utf-8", data="\n".join(r))


mk_settings(
    sp=Path(r"H:\repos\getnovel\src\getnovel\app\settings.py"), sc=get_settings()
)
