import time
import logging

# Selenium import
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

from base64 import b64encode


class SeleniumHelper:

	proxy_type = None
	proxy_host = None
	proxy_port = None
	driver = None
	TIMEOUT = None
	WAIT = None
	DELAY = None

	db = None

	def __init__(self, driver_path, proxy, headless):

		profile = webdriver.FirefoxProfile()

		credentials = proxy['credentials']
		proxy = '' if proxy['proxy'] is None else proxy['proxy']

		profile.set_preference('permissions.default.image', 2)
		profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

		if len(proxy.split(':')) == 2:
			logging.info('Using proxy: {}'.format(proxy))

			proxy_host = proxy.split(':')[0]
			proxy_port = int(proxy.split(':')[1])

			profile.set_preference("network.proxy.type", 1)
			profile.set_preference("network.proxy.ssl", proxy_host)
			profile.set_preference("network.proxy.ssl_port", proxy_port)

			if credentials:
				credentials = b64encode(credentials.encode('ascii')).decode('utf-8')
				profile.set_preference('extensions.closeproxyauth.authtoken', credentials)

		profile.update_preferences()

		options = Options()
		options.headless = headless

		self.driver = webdriver.Firefox(options=options, firefox_profile=profile, executable_path=driver_path)
		self.driver.set_page_load_timeout(self.TIMEOUT)

	def __del__(self):
		if self.driver:
			self.close()

	def src(self):
		return self.driver.page_source

	def loadPage(self, page):
		try:
			self.driver.get(page)
			time.sleep(self.DELAY)
		except Exception as e:
			raise Exception("Can't load page {} - {}".format(page, e))

	def loadAndWait(self, url, selector, wait=None):
		wait = self.WAIT if wait is None else wait
		self.loadPage(url)
		return self.waitShowElement(selector, wait)

	def waitShowElement(self, selector, wait=None):
		try:
			wait = self.WAIT if wait is None else wait
			wait = WebDriverWait(self.driver, wait)
			return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
		except Exception as e:
			raise Exception("Error loading element: {}".format(e))

	def waitShowElementByXPath(self, xpath, wait=None):
		try:
			wait = self.WAIT if wait is None else wait
			wait = WebDriverWait(self.driver, wait)
			return wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
		except Exception as e:
			raise Exception("Error loading element: {}".format(e))

	def getElementFrom(self, fromObject, selector):
		try:
			return fromObject.find_element_by_css_selector(selector)
		except NoSuchElementException:
			return None

	def getElementsFrom(self, fromObject, selector):
		try:
			return fromObject.find_elements_by_css_selector(selector)
		except NoSuchElementException:
			return None

	def getElement(self, selector):
		return self.getElementFrom(self.driver, selector)

	def getElements(self, selector):
		return self.getElementsFrom(self.driver, selector)

	def getElementFromValue(self, fromObject, selector):
		element = self.getElementFrom(fromObject, selector)
		return self.getValue(element)

	def getElementValue(self, selector):
		element = self.getElement(selector)
		if element:
			return self.getValue(element)
		return None

	def waitAndGetElementValue(self, selector):
		if not self.waitShowElement(selector):
			return None
		return self.getElementValue(selector)

	def getValue(self, element):
		if element:
			return element.text
		return None

	def getAttribute(self, element, attribute):
		if element:
			return element.get_attribute(attribute)
		return None

	def changeAttribute(self, element, attr, value):
		self.driver.execute_script("arguments[0].setAttribute('{}','{}')".format(attr, value), element)

	def getElementAttribute(self, selector, attribute):
		element = self.getElement(selector)
		if element:
			return self.getAttribute(element, attribute)
		return None

	def click(self, element):
		self.moveToElement(element)
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.click(element)
		actions.perform()

	def moveToElement(self, element):
		self.driver.execute_script("return arguments[0].scrollIntoView();", element)
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.perform()

	def scrollDown(self):
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	def close(self):
		self.driver.quit()