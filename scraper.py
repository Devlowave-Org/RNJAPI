import requests
from bs4 import BeautifulSoup

from region import *
from database import *


def get_page(url, method, content_link, post_data=None):
    if method == 'GET':
        response = requests.get(url)
    else:
        response = requests.post(url, data=post_data, headers={'Accept-Encoding': ''})
    if response.status_code == 200:
        content = response.text
        with open(content_link, 'w', encoding='utf-8') as file:
            file.write(content)
        print('Page successfully downloaded.')
    else:
        print(f'Download failed. Status code : {response.status_code}')


def open_html(file_link):
    with open(file_link) as html:
        return BeautifulSoup(html, "html.parser")


class ScrapeAllJa:
    URL = "https://juniorassociation.org/juniors-associations"
    FILE_LINK = "./html/all_ja.html"
    TABLE_NAME = "RNJAPI"

    def __init__(self):
        # get_page(ScrapeAllJa.URL, "POST", ScrapeAllJa.FILE_LINK, {"userform": "chercher-JA"})
        self.soup = open_html(ScrapeAllJa.FILE_LINK)
        self.database = Database()
        self.database.create_rnjapi_table(ScrapeAllJa.TABLE_NAME)

    def get_items(self):
        articles = self.get_all_ja()
        for article in articles:
            directory_link = article.a.get("href")
            id = self.collect_ja_id(directory_link)
            name = article.h4.text
            li = article.li.text
            city = self.collect_city(li)
            department_nbr = self.collect_department(li)
            department_name = DEPARTMENTS[department_nbr]
            region = self.collect_region(department_nbr)
            short_description = article.p.text

            data = [id, name, city, department_nbr, department_name, directory_link, region, short_description]
            self.save_items(data)

    def save_items(self, data):
        id = data.pop(0)
        data_tuple = tuple(data)
        bdd_ja_data = self.database.select_data(
            "name, city, department_nbr, department_name, directory_link, region, short_description",
            ScrapeAllJa.TABLE_NAME, f"WHERE id = {id}")
        if bdd_ja_data:
            if not bdd_ja_data[0] == data_tuple:
                self.database.update_rnjapi_all_ja_data(data_tuple + (id,))
        else:
            self.database.insert_rnjapi_all_ja_data((id,) + data_tuple)

    def get_all_ja(self):
        articles = self.soup.findAll("article", class_="mini-fiche ja")
        return articles

    @staticmethod
    def collect_ja_id(link):
        ja_id = ""
        for char in reversed(link):
            if char.isdigit():
                ja_id += char
            else:
                ja_id = "".join(reversed(ja_id))
                return ja_id

    @staticmethod
    def collect_department(string):
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
    def collect_region(department_nbr):
        region_name = ''.join(region_name for region_name, dptm_list in REGIONS.items() if department_nbr in dptm_list)
        return region_name

    @staticmethod
    def collect_city(string):
        city = ''.join(char for char in string if not (char.isdigit() or char in ("(", ")"))).strip()
        return city


class ScrapeJaPage:
    def __init__(self, end_of_url):
        self.url = f"https://juniorassociation.org/{end_of_url}"
        self.file_link = f"./html/ja/{end_of_url}.html"
        get_page(self.url, "GET", self.file_link)
        self.soup = open_html(self.file_link)


scraper = ScrapeAllJa()
scraper.get_items()
