from typing import Any, List
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import requests
from  config import HEADERS


class FetchLinks:
    def __init__(self, urls: list, headers: dict = HEADERS) -> None:
        self.urls = urls
        self.products_per_page = None
        self.headers = headers
        self.links = list()

    @staticmethod
    def get_number_per_page(html:str, index:int=None) -> int:
        """get total number of products per page"""

        soup = BeautifulSoup(html.text, "html.parser")
        product_tag = soup.find(
            "ul", 
            class_ = "products"
        )

        products = product_tag.find_all(
            "product type-product"
        )

        total = len(products)

        print(f"found {total} products in page {index}")

        return total 
   
    
    @staticmethod
    def get_number_of_pages(html: str) -> int:
        """Get the total number of pages found in a url"""
    
        soup = BeautifulSoup(html, "html.parser")
        pagination_tag = soup.find( "nav", class_="woocommerce-pagination")
        if pagination_tag:
            page_numbers = pagination_tag.find_all(
                "a", 
                class_ = "page-numbers"
            )
            last_page = int(page_numbers[-1].text) if page_numbers[-1].text.isdigit() else int(page_numbers[-2].text)
            print(f"Found {last_page} pages")
            return last_page
        raise Exception(0)
    

    @staticmethod
    def get_links(response) -> List:
        """Grab the links for the products for scrapping"""
        
        links = []

        soup = BeautifulSoup(response, "html.parser") 
        product_list = soup.find('ul', class_='products')

        for product_summary in product_list.find_all('li', class_=['product', 'type-product']):
            link = product_summary.find('a', class_='woocommerce-LoopProduct-link')['href']
            links.append(link)
        return links 
    

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Any:
        """Get the raw html data from the page"""
        print(f"Fetching {url}")
        async with session.get(url) as response:
            if response.status != 200: 
                raise Exception(response.status)
            return await response.text()


    def get_link(self, url,index) -> str:
        """Joins the product links with their page number index"""
        return "".join([url, "page/"+str(index)])
    
    
    async def scrape_data(self, url: str) -> Any:
        #create session
        self.mega_links = [] #all product links  in all pages
  
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            initial_response = await self.fetch(session, url)
            for index in range(1, self.get_number_of_pages(initial_response) + 1):
                response = await self.fetch(session, self.get_link(url, index))
                #print(response)
                self.mega_links.extend(self.get_links(response))
            
            print("total product links ", len(self.mega_links))

            """
            self.page_data = [asyncio.create_task(self.fetch(session, url)) for url in self.mega_links]
            results = await asyncio.gather(*self.page_data)
            print(results)
            return results
            """        

    async def main(self):
        """Initiate the web scrapping process"""
        scrapped_data = []
        for url in self.urls:
            data = await self.scrape_data(url)
            scrapped_data.append(data)

        return scrapped_data


#if __name__ == '__main__':
#    urls = [
    #    #"https://rcfminibikes.com/product-category/all/"
    #     'https://offermanwoodshop.com/store/'
    #
    # ]
    # fetcher= FetchLinks(urls)
    # asyncio.run(fetcher.main())
