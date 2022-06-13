from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

CITY_CODES = {
    'MSK': '2398',
    'SPB': '1645',
}


class Parser:
    def __init__(self):
        self._cur_time = None
        self.city_code = None
        self._url = 'https://magnit.ru/promo/'
        self._file_name = None

    def __get_source_html(self):
        file_html = f'{self.city_code}-city_code__{self._cur_time}.html'

        with webdriver.Chrome() as driver:
            driver.get(url=self._url)

            if self.city_code != CITY_CODES['MSK']:
                driver.add_cookie(cookie_dict={'name': 'mg_geo_id', 'value': self.city_code})
                driver.get(url=self._url)

            count = driver.find_element(by=By.CLASS_NAME, value='js-сatalogue__header-text').text.split(' ')[1]
            cards = driver.find_elements(by=By.CLASS_NAME, value='card-sale_catalogue')

            while len(cards) < int(count):
                driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                cards = driver.find_elements(by=By.CLASS_NAME, value='card-sale_catalogue')
            else:
                with open(file_html, 'w', encoding='Utf-8') as f_obj:
                    f_obj.write(driver.page_source)

            return file_html

    def __collect_data(self):

        html_file_name = self.__get_source_html()

        with open(html_file_name, encoding='utf-8') as f_obj:
            soup = BeautifulSoup(f_obj, 'lxml')

        city = soup.find('a', class_='header__contacts-link header__contacts-link_city').text.strip()
        self._file_name = f'{city}_{self._cur_time}.csv'

        cards = soup.find_all('a', class_='card-sale_catalogue')

        data = [('Товар', 'Старая цена', 'Скидка', 'Новая цена', 'Срок действия скидки')]

        for card in cards:
            try:
                card_title = card.find('div', class_='card-sale__title').text.strip()
                card_discount = card.find('div', class_='card-sale__discount').text.strip()
            except AttributeError:
                continue

            card_old_price_integer = card.find('div', class_='label__price_old').find('span',
                                                                                      class_='label__price-integer')
            card_old_price_decimal = card.find('div', class_='label__price_old').find('span',
                                                                                      class_='label__price-decimal')
            card_old_price = f'{card_old_price_integer.text.strip()}.{card_old_price_decimal.text.strip()}'

            card_new_price_integer = card.find('div', class_='label__price_new').find('span',
                                                                                      class_='label__price-integer')
            card_new_price_decimal = card.find('div', class_='label__price_new').find('span',
                                                                                      class_='label__price-decimal')
            card_new_price = f'{card_new_price_integer.text.strip()}.{card_new_price_decimal.text.strip()}'

            card_sale_date = card.find('div', class_='card-sale__date').text.strip().replace('\n', ' ')

            data.append((card_title, card_old_price, card_discount, card_new_price, card_sale_date))

        with open(self._file_name, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        os.remove(html_file_name)

    def run(self, city_code):
        self.city_code = city_code
        self._cur_time = datetime.now().strftime('%d_%m_%Y_%H_%M')
        self.__collect_data()
        return self._file_name


if __name__ == '__main__':
    print(Parser().run('1650'))
