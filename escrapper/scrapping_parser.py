"""
This file contains the parsers that will check the different pages and then
grab the equivalent data
"""

from typing import Any, Dict, List, Tuple
from bs4 import BeautifulSoup
import re

class ParsePage:
    def __init__(self, html_soup) -> None:
        self.soup = html_soup

    def start_parsing(self) -> Dict[str, Any]:
        try:
            product_data = {
                "post_title": self.get_product_name(),
                "post_name": self.generate_slug_name(self.get_product_name()),
                "post_content": self.get_description_html(),
                "post_excerpt": self.get_summary_section(), 
                "_sku": None,
                "_regular_price": self.get_product_price(),
                "images": None,
                "tax:product_cat": self.get_category(),
                "tax:product_tag": None,
            }
            return product_data
        except Exception as e:
            print(f"Error while parsing: {e}")
            return {}

    def get_product_price(self) -> str | None:
        """Get the product price from the product details"""
        try:
            price_element = self.soup.find('p', class_='price')
            if price_element:
                price = price_element.find('bdi').text.strip()
                return price
        except Exception as e:
            print(f"Error fetching product price: {e}")
        return None

    def get_product_name(self) -> str | None:
        """Get the product name from the product details"""
        try:
            name = self.soup.find('h1', class_='product_title').text.strip()
            return name
        except Exception as e:
            print(f"Error fetching product name: {e}")
        return None

    def get_summary_section(self) -> str | None:
        """Get the contents from the summary section"""
        try:
            summary_element = self.soup.find('div', class_='woocommerce-product-details__short-description')
            summary = summary_element.decode_contents().strip() if summary_element else None
            return summary
        except Exception as e:
            print(f"Error fetching summary section: {e}")
        
        return None

    def get_sku(self) -> str | None:
        """Get the SKU text from the product details"""
        try:
            sku = self.soup.find('span', class_='sku').text.strip()
            return sku
        except Exception as e:
            print(f"Error fetching SKU: {e}")
        
        return None


    def get_tags(self) -> List[str] | None:
        """Get the product tags"""
        try:
            categories_element = self.soup.find('span', class_='posted_in')
            tags = [a.text for a in categories_element.find_all('a')]
            return tags

        except Exception as e:
            print(f"Error fetching TAGS: {e}")
        
        return None
        

    def get_description_html(self) -> Any:
        """Get the product description"""
        try:
            product_description = self.soup.find('div', class_=['woocommerce-Tabs-panel', 'woocommerce-Tabs-panel--description', 'panel entry-content'])
            if product_description:
                # Remove only the first <h2> tag from description
                first_h2_tag = product_description.find('h2')
                if first_h2_tag:
                    first_h2_tag.decompose()
                product_description = str(product_description)
            else:
                product_description = str(product_description)

        except Exception as e:
            print(f"Error: {e}")
        
            return None



    def get_additional_information(self) -> Dict | None:
        """Get extra information about the product"""
        try:
            # Find the additional information tab
            additional_info_tab = self.soup.find('li', class_='additional_information_tab')
            
            if additional_info_tab:
                additional_info_content = additional_info_tab.find_next('div', class_='woocommerce-Tabs-panel').decode_contents()

                # Extract the attribute details from additional_info_content
                additional_info_soup = BeautifulSoup(additional_info_content, 'html.parser')
                attribute_elements = additional_info_soup.find_all('tr', class_='woocommerce-product-attributes-item')

                attributes = {}
                for attribute_element in attribute_elements:
                    attribute_label = attribute_element.find('th', class_='woocommerce-product-attributes-item__label').text.strip()
                    attribute_value = attribute_element.find('td', class_='woocommerce-product-attributes-item__value').text.strip()

                    attributes[attribute_label] = attribute_value
                
                return attributes
               
        except Exception as e:
            print(f"Error: {e}")
        
        return None

    def get_images(self) -> Tuple[Any, Any] | None:
        """Get featured images and gallery images for the products"""
        try:
            image_div = self.soup.find('div', class_='woocommerce-product-gallery')
            image_tags = image_div.find_all('img')

            featured_image = image_tags[0]['src'] if image_tags else None
            gallery_images = [img['src'] for img in image_tags[1:]] if len(image_tags) > 1 else None
            
            return (featured_image, gallery_images)
        except Exception as e:
            print(f"Error fetching iMAGES: {e}")
            
        return None


    def get_category(self) -> str | None:
        """Get the category from the last anchor tag"""
        try:
            breadcrumb_nav = self.soup.find('nav', class_='woocommerce-breadcrumb')
            last_a_tag = breadcrumb_nav.find_all('a')[-1]

            category = last_a_tag.text.strip()
            return category
        except Exception as e:
            print(f"Error fetching CATEGORY: {e}")

        return None


    def generate_slug_name(self, name: str):
        """Generate the slug name from the product name"""
        try:
            slug = re.sub(r'\s+', '_', name).lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            return slug
        except Exception as e:
            print(f"Error GENERATING SLUG: {e}")
        
        return None
