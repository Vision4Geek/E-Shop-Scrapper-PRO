# escrapper > main_scrapper.py

"""
This file contains the parsers that will check the different pages and then
grab the equivalent data
"""

from bs4 import BeautifulSoup


class ParsePage:
    def __init__(self, html_soup: BeautifulSoup) -> None:
        self.soup = html_soup

    def start_parsing(self):
        pass

    def get_product_price(self) -> str | None:
        """Get the product price from the product details"""
        try:
            price_element = self.soup.find('p', class_='price')

            # Check if the price element exists and contains a valid price
            if price_element and price_element.text.strip() != '':
                price = price_element.find('bdi').text.strip()
                return price

            return None

        except Exception as e:
            print(f"Error: {e}")
        
        return None

    def get_product_name(self) -> str | None:
        """Get the product name from the product details"""
        try:
            name = self.soup.find('h1', class_='product_title').text.strip()
            return name
        except Exception as e:
            print(f"Error: {e}")
        
        return None



    def get_summary_section(self):
        pass

    def get_sku(self):
        pass

    def get_tags(self):
        pass

    def get_description_html(self):
        pass

    def get_additional_information(self):
        pass

    def get_images(self):
        pass

    def get_category(self):
        pass



    def generate_slug_name(self):
        pass


