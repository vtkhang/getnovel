"""Store the settings of spider for utils crawler. """
from pathlib import Path


def get_settings():
    """Return the settings of spider.

    Returns
    -------
    dict
        Spider settings.
    """
    return {
        "ROBOTSTXT_OBEY": False,
        "SPIDER_MODULES": ["getnovel.app.spiders"],
        "AUTOTHROTTLE_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        },
        "ITEM_PIPELINES": {
            "getnovel.app.pipelines.AppPipeline": 300,
            "getnovel.app.pipelines.CoverImagesPipeline": 200,
        },
        "IMAGES_STORE": f'{Path.home() / "GetNovel" / "images"}',
        "LOG_FORMAT": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        "LOG_SHORT_NAMES": True,
        "LOG_FILE": f'{Path.home() / "GetNovel" / "logs" / "log.txt"}',
        "LOG_FILE_APPEND": False,
    }
