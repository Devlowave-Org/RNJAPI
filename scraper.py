import os
import requests
from bs4 import BeautifulSoup
from urlextract import URLExtract
import re

from region import *
from database import *


class Scraper:
    TABLE_NAME = "RNJAPI"

    def __init__(self):
        self.database = Database()
        self.database.create_rnjapi_table(Scraper.TABLE_NAME)

    @staticmethod
    def create_folder_if_not_exists(folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # noinspection PyBroadException
    @staticmethod
    def get_page(url, method, content_path, post_data=None):
        try:
            if method == 'GET':
                response = requests.get(url)
            else:
                response = requests.post(url, data=post_data, headers={'Accept-Encoding': ''}, stream=True)

            if response.status_code == 200:
                content = response.text
                with open(content_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f'Page {content_path} successfully downloaded.')
            else:
                print(f'Download failed. Status code : {response.status_code}')
        except Exception:
            print(f" Page {url} download error")

    @staticmethod
    def open_html(file_path):
        with open(file_path) as html:
            return BeautifulSoup(html, "html.parser")

    def save_items(self, scraper_name, data, column_name):
        id = data.pop(0)
        data_tuple = tuple(data)
        bdd_ja_data = self.database.select_data(column_name, Scraper.TABLE_NAME, f"WHERE id = {id}")
        if bdd_ja_data:
            if not bdd_ja_data[0] == data_tuple:
                if scraper_name == FirstScraper.CLASS_NAME:
                    self.database.update_rnjapi_first_scraper_data(data_tuple + (id,))
                else:
                    self.database.update_rnjapi_second_scraper_data(data_tuple + (id,))
        elif scraper_name == FirstScraper.CLASS_NAME:
            self.database.insert_rnjapi_first_scraper_data((id,) + data_tuple)


class FirstScraper(Scraper):
    CLASS_NAME = "FirstScraper"
    URL = "https://juniorassociation.org/juniors-associations"
    FOLDER_PATH = "./html/"
    FILE_PATH = "./html/all_ja.html"

    def __init__(self):
        Scraper.__init__(self)
        self.create_folder_if_not_exists(self.FOLDER_PATH)
        self.get_page(FirstScraper.URL, "POST", FirstScraper.FILE_PATH, {"userform": "chercher-JA"})
        self.soup = self.open_html(FirstScraper.FILE_PATH)

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
            self.save_items(FirstScraper.CLASS_NAME, data,
                            "id, name, city, department_nbr, department_name, directory_link, region, short_description")

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


class SecondScraper(Scraper):
    CLASS_NAME = "SecondScraper"
    BASE_URL = "https://juniorassociation.org/"
    FOLDER_PATH = "./html/ja/"

    def __init__(self):
        Scraper.__init__(self)
        self.ja_link_and_id_list = self.database.select_data("id, directory_link", "RNJAPI")
        self.extractor = URLExtract()

    def get_items(self):
        for ja_items in self.ja_link_and_id_list:
            id = ja_items[0]
            link = ja_items[1]
            file_path = f"{self.FOLDER_PATH}{id}.html"
            url = f"{SecondScraper.BASE_URL}{link}"
            self.get_page(url, "GET", file_path)
            soup = self.open_html(file_path)

            description = soup.find("article", class_="page-content").p.text

            div = soup.find("div", class_="infos-generales")
            categories_dict = self.get_categories(div)
            website_urls_dict = self.detect_urls(categories_dict["website"])
            social_networks_urls_dict = self.detect_urls(categories_dict["social_networks"])

            website = ""
            if "other_website" in website_urls_dict.keys() and website_urls_dict["other_website"]:
                website = website_urls_dict["other_website"][0]
                del website_urls_dict["other_website"]

            final_urls_dict = website_urls_dict | social_networks_urls_dict
            email = self.detect_email(categories_dict["contact"])
            approval_date = categories_dict["approval_date"]
            mumbers_nbr = int(categories_dict["mumbers_nbr"].strip())

            data = [id, description, website, final_urls_dict.get("instagram", ""), final_urls_dict.get("facebook", ""),
                    final_urls_dict.get("youtube", ""), final_urls_dict.get("tiktok", ""),
                    final_urls_dict.get("twitter", ""), final_urls_dict.get("discord", ""),
                    str(final_urls_dict.get("other_website", "[]")), email, approval_date, mumbers_nbr]

            self.save_items(SecondScraper.CLASS_NAME, data,
                            "description, website, instagram, facebook, youtube, tiktok, twitter, discord, other_website, email, approval_date, mumbers_nbr")

    # noinspection PyBroadException
    @staticmethod
    def get_categories(div):
        categories = ("Visitez notre site :", "Autres site, réseaux sociaux... :", "Pour nous contacter :",
                      "Date de dernière habilitation :", "Nbre d'adhérents :")
        key = ("website", "social_networks", "contact", "approval_date", "mumbers_nbr")
        categories_dict = {}
        for string, key in zip(categories, key):
            try:
                value = div.find("strong", string=string).parent.text.replace(string, "")
                categories_dict[key] = value
            except Exception:
                categories_dict[key] = ""
        return categories_dict

    def detect_urls(self, string):
        if not string:
            return {}

        urls = self.extractor.find_urls(string, check_dns=True)

        for i, url in enumerate(urls):
            string = string.replace(url, "")
            if "http" not in url:
                urls[i] = "https://" + url

        urls_dict1 = self.sort_urls(urls)
        urls_dict2 = self.detect_social_networks(string)
        final_urls_dict = urls_dict1 | urls_dict2

        return final_urls_dict

    @staticmethod
    def sort_urls(urls_list):
        if not urls_list:
            return {}

        urls_dict = {"other_website": []}
        for url in urls_list:
            social_networks = ("instagram", "facebook", "youtube", "tiktok", "twitter", "discord")
            for social_network in social_networks:
                if f"{social_network}." in url:
                    urls_dict[social_network] = url
                    break
            if url not in urls_dict.values():
                urls_dict["other_website"].append(url)
        return urls_dict

    @staticmethod
    def detect_social_networks(string):
        string = string.strip()
        if not string:
            return {}

        urls_dict = {}
        social_networks = ("instagram", "twitter", "tiktok", "youtube")
        start_urls = ("https://www.instagram.com/", "https://twitter.com/", "https://www.tiktok.com/@",
                      "https://www.youtube.com/@")

        for social_network, start_url in zip(social_networks, start_urls):
            pattern = rf'{social_network}[:;,"\' s]{{2,4}}([a-z0-9_.@\-]{{4,30}})|([a-z0-9_.@\-]{{4,30}})[:;,()"\' s]{{2,6}}{social_network}'
            match = re.search(pattern, string, re.IGNORECASE)

            if match:
                account_name = match.group(1) or match.group(2)
                account_name = account_name.replace("@", "")
                account_url = start_url + account_name
                urls_dict[social_network] = account_url

        return urls_dict

    @staticmethod
    def detect_email(string):
        pattern_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        match = re.search(pattern_email, string)
        if match:
            email = match.group()
            return email
        return ""


scraper1 = FirstScraper()
scraper1.get_items()
scraper2 = SecondScraper()
scraper2.get_items()
