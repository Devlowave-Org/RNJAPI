from database import *
from scrapers import *
from constants import *


class CreateAndCompleteDatabase:
    NEW_BASE_PATH = "./new_html/"
    BASE_PATH = "./html/"

    def __init__(self):
        self.current_date = get_current_date()
        self.table_name = f"{BASE_TABLE_NAME}{self.current_date}"

        try:
            self.ja_list_scraper = JaListScraper(self.NEW_BASE_PATH, True)
        except Exception:
            print("a problem occurred while downloading the ja list page")
            self.ja_list_scraper = JaListScraper(self.BASE_PATH, False)
            copy_file(f"{self.BASE_PATH}{self.ja_list_scraper.FILE_NAME}", f"{self.NEW_BASE_PATH}{self.ja_list_scraper.FILE_NAME}")

        self.main()

    def main(self):
        articles = self.ja_list_scraper.get_all_ja()
        all_items = [self.get_ja_items(article) for article in articles]

        database = Database(TABLE_PATH)
        self.create_table(database)
        self.save_items_into_bdd(all_items, database)
        database.close()

        delete_directory_if_exist(self.BASE_PATH)
        rename_directory(self.NEW_BASE_PATH, self.BASE_PATH)

    def create_table(self, database):
        if is_valid_table(self.table_name):
            database.delete_table(self.table_name)
            sql_command = f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            department_nbr TEXT,
            department_name TEXT,
            region TEXT,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            website TEXT,
            instagram TEXT,
            facebook TEXT,
            youtube TEXT,
            tiktok TEXT,
            twitter TEXT,
            discord TEXT,
            other_website TEXT,
            email TEXT,
            approval_date INTEGER,
            members_nbr INTEGER
            )'''
            database.execute(sql_command)
            database.commit()
        else:
            print("invalid table name")

    def get_ja_items(self, article):
        id_nbr = self.ja_list_scraper.get_ja_id(article)
        name = self.ja_list_scraper.get_ja_name(article)
        city = self.ja_list_scraper.get_ja_city(article)
        department_nbr = self.ja_list_scraper.get_ja_department_nbr(article)
        department_name = DEPARTMENTS[department_nbr]
        end_url = self.ja_list_scraper.get_page_url(article)
        region = ''.join(region_name for region_name, dptm_list in REGIONS.items() if department_nbr in dptm_list)

        ja_list_scraper_items = [id_nbr, name, city, department_nbr, department_name, region, end_url]

        try:
            ja_page_scraper = JaPageScraper(id_nbr, end_url, self.NEW_BASE_PATH, True)
            ja_page_scraper_items = self.get_ja_page_scraper_items(ja_page_scraper)
            return ja_list_scraper_items + ja_page_scraper_items

        except AttributeError or Exception:
            try:
                ja_page_scraper = JaPageScraper(id_nbr, end_url, self.BASE_PATH, False)
                ja_page_scraper_items = self.get_ja_page_scraper_items(ja_page_scraper)
                copy_file(f"{self.BASE_PATH}/ja/{id_nbr}.html", f"{self.NEW_BASE_PATH}/ja/{id_nbr}.html")
                print(f"there is a problem with this page: \n{end_url}\nthe program uses the backup\n")
                return ja_list_scraper_items + ja_page_scraper_items

            except FileNotFoundError:
                print(f"there is a problem with this page: \n{end_url}\nand there is no backup\n")
                delete_file_if_exist(f"{self.NEW_BASE_PATH}{id_nbr}.html")
                return ja_list_scraper_items + [""] * 12

    @staticmethod
    def get_ja_page_scraper_items(ja_page_scraper):
        description = ja_page_scraper.get_ja_description()
        website = ja_page_scraper.get_ja_url("website")
        instagram = ja_page_scraper.get_ja_url("instagram")
        facebook = ja_page_scraper.get_ja_url("facebook")
        youtube = ja_page_scraper.get_ja_url("youtube")
        tiktok = ja_page_scraper.get_ja_url("tiktok")
        twitter = ja_page_scraper.get_ja_url("twitter")
        discord = ja_page_scraper.get_ja_url("discord")
        other_website = str(ja_page_scraper.get_ja_url("other_website"))
        email = ja_page_scraper.get_ja_email()
        approval_date = ja_page_scraper.get_ja_approval_date()
        members_nbr = ja_page_scraper.get_ja_members_nbr()

        return [description, website, instagram, facebook, youtube, tiktok, twitter, discord, other_website, email,
                approval_date, members_nbr]

    def save_items_into_bdd(self, data_list, database):
        if is_valid_table(self.table_name):
            data_tuple = tuple(data_list)
            sql_command = f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            database.executemany(sql_command, data_tuple)
            database.commit()
        else:
            print("invalid table name")


class Main():
    def __init__(self):

        CreateAndCompleteDatabase()