# flake8: noqa: E501
BOT_NAME = r"GetNovel"
ROBOTSTXT_OBEY = False
SPIDER_MODULES = ['getnovel.app.spiders']
USER_AGENT = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
ITEM_PIPELINES = {
    "getnovel.app.pipelines.AppPipeline": 300,
    "getnovel.app.pipelines.CoverImagesPipeline": 200
}
IMAGES_STORE = r"C:\Users\varus\GetNovel\images"
LOG_FORMAT = r"%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_SHORT_NAMES = True
LOG_FILE = r"C:\Users\varus\GetNovel\logs\log.txt"
LOG_FILE_APPEND = False
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
