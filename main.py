from database import *
from scrapers import *


class CreateAndCompleteDatabase:
    TABLE_PATH = "rnjapi.db"

    def __init__(self):
        self.current_date = get_current_date()
        self.database = Database(CreateAndCompleteDatabase.TABLE_PATH)
        self.table_name = f"RNJAPI_{self.current_date}"
        self.first_scraper = JaListScraper()
        self.main()

    def main(self):
        ja_articles = self.first_scraper.get_all_ja()
        self.create_table()
        all_items = []
        for article in ja_articles:
            ja_items = self.get_ja_items(article)
            all_items.append(ja_items)
        self.save_items_into_bdd(all_items)
        self.database.close()

    def create_table(self):
        self.database.delete_table(self.table_name)
        sql_command = f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
        id INTEGER PRIMARY KEY,
        name TEXT,
        city TEXT,
        department_nbr TEXT,
        department_name TEXT,
        region TEXT,
        page_link TEXT UNIQUE NOT NULL,
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
        self.database.execute_and_commit(sql_command)

    def get_ja_items(self, article):
        id_nbr = self.first_scraper.get_ja_id(article)
        name = self.first_scraper.get_ja_name(article)
        city = self.first_scraper.get_ja_city(article)
        department_nbr = self.first_scraper.get_ja_department_nbr(article)
        department_name = DEPARTMENTS[department_nbr]
        page_link = self.first_scraper.get_page_link(article)
        region = ''.join(region_name for region_name, dptm_list in REGIONS.items() if department_nbr in dptm_list)

        second_scraper = JaPageScraper(id_nbr, page_link)

        description = second_scraper.get_ja_description()
        website = second_scraper.get_ja_url("website")
        instagram = second_scraper.get_ja_url("instagram")
        facebook = second_scraper.get_ja_url("facebook")
        youtube = second_scraper.get_ja_url("youtube")
        tiktok = second_scraper.get_ja_url("tiktok")
        twitter = second_scraper.get_ja_url("twitter")
        discord = second_scraper.get_ja_url("discord")
        other_website = str(second_scraper.get_ja_url("other_website"))
        email = second_scraper.get_ja_email()
        approval_date = second_scraper.get_ja_approval_date()
        members_nbr = second_scraper.get_ja_members_nbr()

        return [id_nbr, name, city, department_nbr, department_name, region, page_link, description, website,
                instagram, facebook, youtube, tiktok, twitter, discord, other_website, email, approval_date,
                members_nbr]

    def save_items_into_bdd(self, data_list):
        data_tuple = tuple(data_list)
        sql_command = f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.database.executemany_and_commit_data(sql_command, data_tuple)


CreateAndCompleteDatabase()
