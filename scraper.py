import requests
from bs4 import BeautifulSoup
from region import *


def get_page(url):
    content = ""
    response = requests.post(url, data={"userform": "chercher-JA"}, headers={'Accept-Encoding': ''})

    if response.status_code == 200:
        content = response.text

        with open('page.html', 'w', encoding='utf-8') as file:
            file.write(content)
        print('Page successfully downloaded.')
    else:
        print(f'Download failed. Status code : {response.status_code}')

    return content


def open_html(file_link="page.html"):
    with open(file_link) as html:
        return BeautifulSoup(html, "html.parser")


class GlobalScraper:
    URL = "https://juniorassociation.org/juniors-associations"

    def __init__(self):
        # self.page_data = get_page(GlobalScraper.URL)
        self.soup = open_html()
        self.sort_items()

    def sort_items(self):
        articles = self.get_all_ja()
        ja_data = []
        for article in articles:
            items_list = []
            link = article.a.get("href")
            ja_id = self.get_ja_id(link)
            li = article.li.text
            department_nbr = self.get_department(li)
            department_name = DEPARTMENTS[department_nbr]
            region = self.get_region(department_nbr)
            city = self.get_city(li)
            name = article.h4.text
            short_description = article.p.text

            var_list = [link, ja_id, li, department_nbr, department_name, region, city, name, short_description]

            for var in var_list:
                items_list.append(var)
            ja_data.append(items_list)
            print(ja_data)

    def get_all_ja(self):
        articles = self.soup.findAll("article", class_="mini-fiche ja")
        return articles

    @staticmethod
    def get_ja_id(link):
        ja_id = ""
        for char in reversed(link):
            if char.isdigit():
                ja_id += char
            else:
                return ja_id

    @staticmethod
    def get_department(string):
        department = ""
        for char in reversed(string):
            if not char.isspace():
                department += char
            else:
                break
        department = "".join(reversed(department)).strip()
        for char in "()":
            department = department.replace(char, "").strip()
        return department

    @staticmethod
    def get_region(department_nbr):
        region_name = ''.join(region_name for region_name, dptm_list in REGIONS.items() if department_nbr in dptm_list)
        return region_name

    @staticmethod
    def get_city(string):
        city = ''.join(char for char in string if not (char.isdigit() or char in ("(", ")"))).strip()
        return city



scraper = GlobalScraper()
