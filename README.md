# alibaba-crawler
Alibaba selenium crawler

## Requirements

1. Python 3.6
2. geckodriver
3. Firefox

## Install
1. Install python. Create python folder and python_folder/Scripts to PATH environment variable (you can do it with enabling \"Add Python 3.6 to PATH\" checkbox while python installation).
2. Download geckodriver https://github.com/mozilla/geckodriver/releases and unzip it.
3. Install Firefox.
4. Run CMD and go to crawler folder ``cd C:/path/to/alibaba-crawler``. Run ``pip install -r requirements.txt``
5. Edit config.ini file ``[CRAWLER]`` section. Set ``driver_path = <path to your geckodriver.exe>`` (You can just copy and paste geckodriver.exe into crawler root folder, so you don't need to edit driver_path field in config.ini). 
If you want to use proxy, set ``proxy = https://host:port``.
6. Edit config.ini file ``[MAIN]`` section. ``min_price``, ``max_price`` - filter params. ``input``, ``output`` - input and output files.

## Usage

``
python app.py
``
