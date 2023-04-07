import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver


class TrackedTea:
    def __init__(self, url, ready: bool = True):
        self.price_new = 0  # 0 значит что цены нет
        self.price_old = 0
        self.url = url
        self.ready = ready
        self.ua = UserAgent()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f"user-agent={self.ua.chrome}")
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(
            executable_path=r"C:\Users\Misha\PycharmProjects\pythonBotTea\chromedriver_\chromedriver.exe",
            options=self.options
        )

    def get_data(self):
        try:
            self.driver.get(self.url)
            source = self.driver.page_source
            soup = BeautifulSoup(source, "lxml")
            class_template = re.compile(r"sc-ikPAEB sc-ksXiFW (?:gZEkPY|kqlxSN) lcozZv")
            template = re.compile(r"price-(?:new|old)(?!-)")
            prices = soup.find("div", class_=class_template).findAll("div", class_=template)
            if len(prices) == 1:
                self.price_new = prices[0].text
                self.price_old = prices[0].text
            else:
                self.price_new = prices[0].text
                self.price_old = prices[1].text
        except Exception as e:
            print(e)
        finally:
            self.driver.close()
            self.driver.quit()
