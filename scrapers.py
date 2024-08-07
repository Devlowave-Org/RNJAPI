import requests
from bs4 import BeautifulSoup
from urlextract import URLExtract
import re

from utils import *


class Scraper:

    def __init__(self, base_path):
        self.jas_folder_path = base_path + "ja/"
        create_folder_if_not_exists(self.jas_folder_path)

    @staticmethod
    def download_page(url, method, content_path, post_data=None, timeout=10):
        try:
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            else:
                response = requests.post(url, data=post_data, headers={'Accept-Encoding': ''}, stream=True, timeout=timeout)

            if response.status_code == 200:
                content = response.text
                with open(content_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f'Page {content_path} successfully downloaded.')
            else:
                print(f'Download failed. Status code: {response.status_code}')
        except requests.exceptions.Timeout:
            print('Download failed. The request timed out.')
        except requests.exceptions.RequestException as e:
            print(f'Download failed. An error occurred: {e}')

    @staticmethod
    def open_html(file_path):
        with open(file_path) as html:
            return BeautifulSoup(html, "html.parser")


class JaListScraper(Scraper):
    URL = "https://juniorassociation.org/juniors-associations"
    FILE_NAME = "all_ja.html"

    def __init__(self, base_path, download):
        super().__init__(base_path)
        file_path = base_path + self.FILE_NAME
        if download:
            self.download_page(JaListScraper.URL, "POST", file_path, {"userform": "chercher-JA"})
        self.soup = self.open_html(file_path)

    def get_all_ja(self):
        return self.soup.findAll("article", class_="mini-fiche ja")

    @staticmethod
    def get_page_url(article):
        return article.a.get("href")

    def get_ja_id(self, article):
        string = self.get_page_url(article)
        match = re.search(r'(\d+)($)', string)
        return match.group(1) if match else "error getting id"

    @staticmethod
    def get_ja_name(article):
        return article.h4.text

    @staticmethod
    def get_ja_city(article):
        string = article.li.text
        match = re.search(r'[^0-9()]+', string)
        return match.group().strip() if match else None

    @staticmethod
    def get_ja_department_nbr(article):
        string = article.li.text
        match = re.search(r'(\()([0-9]+)(\)$)', string)
        return match.group(2) if match else None


class JaPageScraper(Scraper):
    BASE_URL = "https://juniorassociation.org/"

    def __init__(self, id_nbr, end_url, base_path, download):
        super().__init__(base_path)
        self.extractor = URLExtract()
        file_path = f"{self.jas_folder_path}{id_nbr}.html"
        url = f"{JaPageScraper.BASE_URL}{end_url}"
        if download:
            self.download_page(url, "GET", file_path)
        self.soup = self.open_html(file_path)
        self.categories_dict = self.get_categories()
        self.urls_dict = self.get_urls()

    def get_categories(self):
        div = self.soup.find("div", class_="infos-generales")
        categories = ("Visitez notre site :", "Autres site, réseaux sociaux... :", "Pour nous contacter :",
                      "Date de dernière habilitation :", "Nbre d'adhérents :")
        key = ("website", "social_networks", "contact", "approval_date", "members_nbr")
        categories_dict = {}
        for string, key in zip(categories, key):
            try:
                value = div.find("strong", string=string).parent.text.replace(string, "")
                categories_dict[key] = value
            except AttributeError:
                categories_dict[key] = ""
        return categories_dict

    def get_urls(self):
        website_urls_list, website_urls_string = self.detect_urls(self.categories_dict["website"])
        social_networks_urls_list, social_networks_urls_string = self.detect_urls(
            self.categories_dict["social_networks"])

        sorted_website_urls_dict = self.sort_urls(website_urls_list)
        sorted_social_networks_urls_dict = self.sort_urls(social_networks_urls_list)

        detected_social_networks_urls_dict = self.detect_social_networks(social_networks_urls_string)

        if sorted_website_urls_dict["other_website"]:
            sorted_website_urls_dict["website"] = sorted_website_urls_dict["other_website"][0]

        final_urls_dict = sorted_website_urls_dict | sorted_social_networks_urls_dict | detected_social_networks_urls_dict

        return final_urls_dict

    def detect_urls(self, string):
        urls_list = self.extractor.find_urls(string, check_dns=True)

        for i, url in enumerate(urls_list):
            string = string.replace(url, "")
            if "http" not in url:
                urls_list[i] = "https://" + url

        return urls_list, string

    @staticmethod
    def sort_urls(urls_list):
        urls_dict = {"other_website": []}
        for url in urls_list:
            social_networks = ("instagram", "facebook", "youtube", "tiktok", "twitter", "discord")
            for social_network in social_networks:
                if f"{social_network}." in url:
                    urls_dict[social_network] = url
                    break
            if url not in urls_dict.values():
                urls_dict["other_website"].append(url)

        if not urls_dict["other_website"]:
            urls_dict["other_website"] = ""

        return urls_dict

    @staticmethod
    def detect_social_networks(string):
        string = string.strip()

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

    def get_ja_description(self):
        return self.soup.find("article", class_="page-content").p.text

    def get_ja_url(self, category_key):
        return self.urls_dict.get(category_key, "")

    def get_ja_email(self):
        string = self.categories_dict["contact"]
        pattern_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        match = re.search(pattern_email, string)
        return match.group() if match else None

    def get_ja_approval_date(self):
        return self.categories_dict["approval_date"]

    def get_ja_members_nbr(self):
        return int(self.categories_dict["members_nbr"].strip())
