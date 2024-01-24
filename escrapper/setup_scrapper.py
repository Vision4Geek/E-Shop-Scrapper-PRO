from typing import Any, List
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio

from escrapper.config import HEADERS


class FetchLinks:
    def __init__(self, urls: list, products_per_page:int = 16, headers: dict = HEADERS) -> None:
        self.urls = urls
        self.products_per_page = products_per_page
        self.headers = headers
        self.links = list()
   
    
    @staticmethod
    def get_number_of_pages(url: str, products_per_page: int) -> int:
        """Get the total number of pages found in a url"""
        response = requests.get(url + "1", HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        pagination_info = soup.find("nav", class_="woocommerce-pagination")

        if not pagination_info:
            return 0
        
        page_numbers = pagination_info.find_all("a", "page-numbers")

        if not page_numbers:
            return 0
        
        # Get the total number of products based on the last page number
        total_products = int(page_numbers[-2].text) * products_per_page

        total_pages = (total_products - 1) // products_per_page + 1

        return total_pages
    

    @staticmethod
    def get_links(url: str, no_of_pages: int) -> List:
        """Grab the links for the products for scrapping"""
        links = []

        for page in range(1, no_of_pages):
            response = requests.get("".join([url, str(page)]), HEADERS)
            soup = BeautifulSoup(response.text, "html.parser") 
            product_list = soup.find_all('div', class_='wpbf-woo-loop-summary')
            for product_summary in product_list:
                # Extract the href link from the <a> tag
                link = product_summary.find('a', class_='woocommerce-LoopProduct-link')['href']
                links.append(link)

        return links

    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Any:
        print(f"Fetching {url}")
        async with session.get(url) as response:
            return await response.text
    
    
    async def scrape_data(self, url: str) -> Any:
        # initiate links
        links = self.get_links(url, self.get_number_of_pages(url, self.products_per_page))

        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.page_data = [asyncio.create_task(self.fetch(session, url)) for url in links]
            results = await asyncio.gather(*self.page_data)
            return results
        

    async def main(self):
        for url in self.urls:
            data = await self.scrape_data(url)
            # I don't know what can be done with the data here
