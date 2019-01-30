# alibaba-crawler
Alibaba selenium crawler

## Requirements

1. Python 3.6
2. geckodriver
3. Firefox

## Install
1. Install python. Create python folder and python_folder/Scripts to PATH environment variable.
2. Download geckodriver https://github.com/mozilla/geckodriver/releases and unzip.
3. Install Firefox.
4. Run CMD and go to crawler folder ``cd C:/path/to/alibaba-crawler``. Run ``pip install -r requirements.txt``
5. Edit config.ini file ``[CRAWLER]`` section. Set ``driver_path = <path to your geckodriver.exe>``. 
If you want to use proxy, set ``proxy = https://host:port``.
6. Edit config.ini file ``[MAIN]`` section. ``min_price``, ``max_price`` - filter params. ``input``, ``output`` - input and output files.

## Usage

``
python app.py
``
