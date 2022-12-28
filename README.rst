GETNOVEL
========

.. image:: https://img.shields.io/badge/python-3.7+-blue
  :target: https://www.python.org/

.. image:: https://img.shields.io/badge/scrapy-2.5.1+-blue
  :target: https://scrapy.org/

Developer
=========

- Email: vuthuakhangit@gmail.com

Description
===========

- This tool can get text from websites and create epub.
- This project is for research purposes only.

Installation
============

1. Download or clone this project.
2. Make sure Python 3.7 or above is installed.
3. Go to root folder of this project, using pip to install:

  .. code:: bash

    pip install -e .

Development
===========

1. Download or clone this project.
2. Go to to root folder of this project.
3. Using pip to install this project in development mode (better with virtual env like conda):

  .. code:: bash

    pip install -e .[dev]

Build
=====

1. Download or clone this project.
2. Go to to root folder of this project.
3. Install and build this project with package "build":

  .. code:: bash

    pip install build
    python -m build

Ussage
======

- Commands

  .. code:: bash

    getnovel crawl https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

    getnovel convert /path/to/raw/directory

    getnovel epub from_url https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

    getnovel epub from_raw /path/to/raw/directory

- Examples:

  - Create epub fron the input link:

    .. code:: bash

      getnovel epub from_url https://www.ptwxz.com/bookinfo/12/12450.html

  - Download from chapter 1 to chapter 5:

    .. code:: bash

      getnovel crawl --start 1 --stop 5 https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa

  - Download all chapters:

    .. code:: bash

      getnovel crawl https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa

  - Download from chapter 10 to the end of the novel:

    .. code:: bash

      getnovel --start 10 https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa

- Use getnovel package as script

  - Download novel via NovelCrawler

    ::

      from getnovel.utils.crawler import NovelCrawler
      p = NovelCrawler(url="https://truyen.tangthuvien.vn/doc-truyen/truong-da-du-hoa")
      p.crawl(rm_raw=True, start_chap=3, stop_chap=8)

  - Convert txt to xhtml by FileConverter:

    ::

      from getnovel.utils.file import FileConverter
      c = FileConverter(raw_dir_path="/path/to/raw/dir")
      c.convert_to_xhtml(dedup=False, rm_result=True, lang_code="vi")

  - Create epub from the input link:

    ::

      from getnovel.utils.epub import EpubMaker
      e = EpubMaker()
      e.from_url("https://truyen.tangthuvien.vn/doc-truyen/thai-at", dedup=False, start=1, stop=-1)

Supported websites
==================

1. `https://bachngocsach.com/reader/ <https://bachngocsach.com/reader>`_
2. `https://dtruyen.com/ <https://dtruyen.com/>`_
3. `https://metruyencv.com/ <https://metruyencv.com>`_
4. `https://www.ptwxz.com/ <https://www.ptwxz.com>`_
5. `https://www.69shu.com/ <https://www.69shu.com>`_
6. `https://sstruyen.com/ <https://sstruyen.com>`_
7. `https://truyen.tangthuvien.vn/ <https://truyen.tangthuvien.vn/>`_
8. `https://truyenchu.vn/ <https://truyenchu.vn/>`_
9.  `https://truyenfull.vn/ <https://truyenfull.vn>`_
10. `https://truyenyy.vip/ <https://truyenyy.vip/>`_
11. `https://www.uukanshu.com/ <https://www.uukanshu.com>`_


Frameworks, packages and IDEs
=============================

- `Scrapy <https://scrapy.org>`_

- `BeautifulSoup4 <https://www.crummy.com/software/BeautifulSoup>`_
