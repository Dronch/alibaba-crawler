import configparser
from SeleniumTools import AlibabaSelenium

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    crawler = AlibabaSelenium(driver_path=config['CRAWLER']['driver_path'],
                              request_delay=int(config['CRAWLER']['request_delay']),
                              wait_time=int(config['CRAWLER']['read_timeout']),
                              timeout=int(config['CRAWLER']['connect_timeout']),
                              proxy={'proxy': config['CRAWLER']['proxy'], 'credentials': ''},
                              headless=True if str(config['CRAWLER']['headless']).lower() == 'true' else False)

    filename = config['MAIN']['output']
    out = open(filename, 'w')
    out.write('store;url;description;price\n')
    out.close()

    min_price = float(config['MAIN']['min_price'])
    max_price = float(config['MAIN']['max_price'])

    assert min_price < max_price, 'Min price is greater than max price, fix config'

    for url in open(config['MAIN']['input']).read().splitlines():
        items = crawler.crawl(url, filename, min_price, max_price)
