# NOVELUTILS

![python version](https://img.shields.io/badge/python-3.7-blue) ![scrapy version](https://img.shields.io/badge/scrapy-2.5.1-blue)

## Developer

- Email: kdekiwis1@gmail.com

## Description

- This tool can get text from websites and create epub.
- This project is for research purposes only.

## Installation

Using pip to install:

  ```bash
  pip install novelutils
  ```

## Development

1. Clone this repos.

2. Change directory to the project directory.

3. Using these commands to install this package locally:

```bash
pip install -r requirements/dev.txt
pip install -e .
```

## Ussage

- Commands

  ```bash
  novelutils crawl https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

  novelutils convert /path/to/raw/directory

  novelutils epub from_url https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

  novelutils epub from_raw /path/to/raw/directory
  ```

- Examples:

    - Create epub fron the input link:

    ```shell
    novelutils epub from_url https://www.ptwxz.com/bookinfo/12/12450.html
    ```

    - Download from chapter 1 to chapter 5:

    ```shell
    novelutils crawl --start 1 --stop 5 https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa
    ```

    - Download all chapters:

    ```shell
    novelutils crawl https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa
    ```

    - Download from chapter 10 to the end of the novel:

    ```shell
    novelutils --start 10 https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa
    ```

- Use novelutils package as script

    - Download novel via NovelCrawler

    ```python
    from novelutils.utils.crawler import NovelCrawler
    p = NovelCrawler(url="https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa")
    p.crawl(rm_raw=True, start_chap=3, stop_chap=8) 
    ```

    - Convert txt to xhtml by FileConverter:

    ```python
    from novelutils.utils.file import FileConverter
    c = FileConverter(raw_dir_path="/path/to/raw/dir")
    c.convert_to_xhtml(duplicate_chapter=False, rm_result=True, lang_code="vi")
    ```

    - Create epub from the input link:

    ```python
    from novelutils.utils.epub import EpubMaker
    e = EpubMaker()
    e.from_url("https://truyen.tangthuvien.vn/doc-truyen/thai-at", duplicate_chapter=False, start=1, stop=-1)
    ```

## Supported websites

1. [https://truyen.tangthuvien.vn/](https://truyen.tangthuvien.vn/)

2. [https://bachngocsach.com/reader/](https://bachngocsach.com/reader/)

3. [https://webtruyen.com/](https://webtruyen.com/)

4. [https://sstruyen.com/](https://sstruyen.com/)

5. [https://truyenfull.vn/](https://truyenfull.vn/)

6. [https://truyendkm.com/](https://truyendkm.com/)

7. [https://truyencv.com/](https://truyencv.com/) , TruyenCV will take users to their others domains:

  - <del> [https://metruyenchu.com/](https://metruyenchu.com/) </del> (blocked by CloudFlare)

  - [https://vtruyen.com/](https://vtruyen.com/)

  - [https://nuhiep.com/](https://nuhiep.com/)

8. [https://www.69shu.com/](https://www.69shu.com/)

9. [https://www.uukanshu.com/](https://www.uukanshu.com/)

10. [https://www.ptwxz.com/](https://www.ptwxz.com/)


## Frameworks and packages, and IDEs are used in this project:

1. Package, framework:

- [Scrapy](https://scrapy.org/)

- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

2. IDEs:

- [Pycharm Community](https://www.jetbrains.com/pycharm/download)