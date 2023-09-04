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

- This package can be installed via github:

  .. code:: bash

    pip install git+https://github.com/vtkhang/getnovel.git

Supported websites
==================

1. `https://bachngocsach.com.vn/reader <https://bachngocsach.com.vn/reader>`_
2. `https://dtruyen.com/ <https://dtruyen.com/>`_
3. `https://metruyencv.com/ <https://metruyencv.com/>`_
4. `https://www.piaotian.com <https://www.piaotian.com>`_
5. `https://www.69shuba.com <https://www.69shuba.com>`_
6. `https://sstruyen.vn/ <https://sstruyen.vn/>`_
7. `https://truyen.tangthuvien.vn <https://truyen.tangthuvien.vn>`_
8. `https://truyenchu.vn/ <https://truyenchu.vn/>`_
9.  `https://truyenfull.vn <https://truyenfull.vn>`_
10. `https://truyenyy.vip/ <https://truyenyy.vip/>`_
11. `https://www.uukanshu.com <https://www.uukanshu.com>`_

Command line mode
=================

- Commands

  .. code:: bash

    getnovel crawl https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

    getnovel convert /path/to/raw/directory

    getnovel epub from_url https://truyen.tangthuvien.vn/doc-truyen/dichthe-gioi-hoan-my

    getnovel epub from_raw /path/to/raw/directory

- Examples:

  - Create epub from the input link:

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

Frameworks, packages and IDEs
=============================

- `Scrapy <https://scrapy.org>`_
- `Pillow <https://python-pillow.org/>`_
- `tldextract <https://github.com/john-kurkowski/tldextract>`_
- `pytz <https://pypi.org/project/pytz/>`_
- `ipython <https://ipython.org/>`_
- `black <https://github.com/psf/black>`_
- `ruff <https://github.com/astral-sh/ruff>`_
- `prospector <https://prospector.landscape.io/en/master/>`_
- `sphinx <https://www.sphinx-doc.org/en/master/>`_
- `sphinx_rtd_theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_
- `numpydoc <https://numpydoc.readthedocs.io/en/latest/install.html>`_
- `build <https://pypi.org/project/build/>`_
- `python-slugify <https://pypi.org/project/python-slugify/>`_

Development
===========

1. Download or clone this project.
2. Go to to root folder of this project.
3. Using pip to install this project in development mode (better with virtual env like conda):

  .. code:: bash

    pip install -e ".[dev]"
