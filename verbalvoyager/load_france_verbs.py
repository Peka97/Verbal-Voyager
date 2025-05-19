from csv import Error
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from urllib3.exceptions import ReadTimeoutError
from selenium.common.exceptions import TimeoutException, WebDriverException


BASE_URL = 'https://www.babla.ru'
current_port = 10000
letter_url_pattern = BASE_URL + '/спряжения/французский/{letter}/{page_num}'


def get_options():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Обход защиты и оптимизация
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Для Docker/Linux
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--incognito")

    # Отключаем автоматизацию
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return options


def get_driver(options):
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(15)
    return driver


def get_page_soup(url):
    global driver

    driver_not_gutted = True

    while driver_not_gutted:
        print('Page loading...')
        try:
            driver.get(url)
            if "Just a moment..." in driver.page_source:
                raise WebDriverException("Just a moment...")
        except (WebDriverException, TimeoutException):
            print('Error. Try again...')
            time.sleep(5)
            driver.quit()
            print('Driver stop.')
            driver = get_driver(options)
            print('Driver start.')
            time.sleep(5)
        else:
            driver_not_gutted = False

    time.sleep(5)
    print('Page was load.')

    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    print('Cache clear.')

    while "Just a moment..." in driver.page_source:
        print('Waiting...')
        driver.refresh()
        time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print('Driver quit.')
    return soup


def get_header_words(soup):
    header = soup.find('div', {'class': 'quick-results container'})
    if not header:
        print(soup)
    words = header.find_all('div', {'class': 'quick-result-entry'})
    return [
        element.find('li').text
        for element in words
    ]


def get_footer_words(soup):
    indicatif_present_block = soup.find('div', {'class': 'conj-tense-block'})
    return [
        element.text
        for element in indicatif_present_block.find_all(
            'div',
            {'class': 'conj-result'}
        )
    ]


def get_word(url):
    print(f'[URL] {url}')

    soup = get_page_soup(url)

    if 'Не найдены результаты для' in soup.text:
        return

    infinitive, \
        participe_present, \
        participe_passe = get_header_words(soup)
    print(f'[WORD] {infinitive}')

    word_obj = FrenchWord.objects.filter(word=infinitive)
    if not word_obj.exists():
        print(f'[WORD] {infinitive} not exists. Creating word...')
        FrenchWord(word=infinitive).save()

    infinitive = word_obj.first()

    indicatif_j, \
        indicatif_tu, \
        indicatif_il, \
        indicatif_nous, \
        indicatif_vous, \
        indicatif_ils = get_footer_words(soup)

    return FrenchVerb(
        infinitive=infinitive,
        participe_present=participe_present,
        participe_passe=participe_passe,
        indicatif_j=indicatif_j,
        indicatif_tu=indicatif_tu,
        indicatif_il=indicatif_il,
        indicatif_nous=indicatif_nous,
        indicatif_vous=indicatif_vous,
        indicatif_ils=indicatif_ils
    )


# def save_words(words):
#     from django.db import transaction

#     with transaction.atomic():
#         for verb in words:
#             verb.save()


def collect_urls(letter, page_num):
    url = letter_url_pattern.format(letter=letter, page_num=page_num)
    soup = get_page_soup(url)
    if driver.current_url[-1] != url[-1]:
        print(f"Произошло перенаправление на: {driver.current_url}")
        return None
    urls_wrapper = soup.find('div', {'class': 'dict-select-wrapper'})
    urls = urls_wrapper.find_all('a')
    return [url.get('href') for url in urls]


if __name__ == '__main__':

    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verbalvoyager.settings')
    django.setup()
    from dictionary.models import FrenchWord, FrenchVerb
    # load_words_from_site()

    # with open('./urls.json', 'w') as file:
    #     json.dump(load_words_from_site(), file, indent=4)

    # urls = get_urls()
    # for url in urls:
    service = Service(ChromeDriverManager().install())
    options = get_options()

    lowercase_letters = list('qrstuvwxyz')

    for letter in lowercase_letters:
        page_num = 1

        while page_num > 0:
            print(f'[CURRENT] {letter}:{page_num}')

            with get_driver(options) as driver:
                urls = collect_urls(letter, page_num)

            time.sleep(5)

            if not urls:
                break
            print('Urls collected...')

            for url in urls:

                word = url.split('/')[-1]
                if FrenchVerb.objects.filter(infinitive__word=word).exists():
                    print(f'[VERB] {word}-verb exists. Skipping...')
                    continue

                with get_driver(options) as driver:
                    word = get_word(BASE_URL + url)
                time.sleep(5)
                if not word:
                    continue

                word.save()
                print(f'[WORD] {word.infinitive} was collected.')

            page_num += 1
    # words = []

    # for url in urls:
    #     word = get_word(url)
    #     print(f'[WORD] {word.infinitive} was collected.')
    #     words.append(word)

    # save_words([word,])

    driver.quit()
