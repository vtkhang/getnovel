"""These settings only use for scrapy shell."""

from pathlib import Path

hp = Path.home()
imgp = hp / "GetNovel" / "images"
lp = hp / "GetNovel" / "logs"
save_path = hp / "GetNovel" / "crawled"
imgp.mkdir(parents=True, exist_ok=True)
lp.mkdir(parents=True, exist_ok=True)
# flake8: noqa
BOT_NAME = r"GetNovel"
ROBOTSTXT_OBEY = False
SPIDER_MODULES = ["getnovel.app.spiders"]
USER_AGENT = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "\
             "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54"
ITEM_PIPELINES = {
    "getnovel.app.pipelines.AppPipeline": 300,
    "getnovel.app.pipelines.CoverImagesPipeline": 200,
}
IMAGES_STORE = str(imgp)
DOWNLOADER_MIDDLEWARES = {"getnovel.app.middlewares.AppDownloaderMiddleware": 500}
LOG_FORMAT = r"%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_SHORT_NAMES = True
LOG_LEVEL = r"DEBUG"
LOG_FILE = str(lp / "shell.log")
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 6
DOWNLOAD_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
COOKIES_DEBUG = True
SAVE_PATH = str(save_path)
