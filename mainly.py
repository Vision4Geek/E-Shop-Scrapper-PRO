import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
from datetime import datetime, timedelta
import csv
import subprocess
from tabulate import tabulate
import re, os
import pandas as pd


class EScraperPRO:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers
        self.productlinks = []
        self.data = []
        self.categories = []
        self.products_per_page = 16

    def generate_random_date(self):
        start_date = datetime(2022, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
        formatted_date = random_date.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date

    def get_total_products(self):
        response = requests.get(self.base_url + "1", headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        pagination_info = soup.find('nav', class_='woocommerce-pagination')

        if pagination_info:
            page_numbers = pagination_info.find_all('a', class_='page-numbers')
            last_page = int(page_numbers[-2].text) if page_numbers else 0
            total_products = last_page * self.products_per_page
        else:
            total_products = 0

        total_pages = (total_products - 1) // self.products_per_page + 1
        return total_pages

    def scrape_product_links(self, total_pages):
        for page in tqdm(range(1, total_pages + 1), desc='Scraping Pages'):
            url = self.base_url + str(page)
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_list = soup.find_all('div', class_='wpbf-woo-loop-summary')

            for product_summary in product_list:
                post_title = product_summary.find('h3', class_='woocommerce-loop-product__title').text
                link = product_summary.find('a', class_='woocommerce-LoopProduct-link')['href']
                self.productlinks.append(link)

    def scrape_product_data(self):
        for link in tqdm(self.productlinks, desc='Scraping Products'):
            try:
                f = requests.get(link, headers=self.headers).text
                hun = BeautifulSoup(f, 'html.parser')
                
                price_element = hun.find('p', class_='price')
                price = price_element.find('bdi').text.strip() if price_element and price_element.text.strip() != '' else None
                
                name = hun.find('h1', class_='product_title').text.strip() if hun.find('h1', class_='product_title') else None
                
                slug = re.sub(r'\s+', '_', name).lower() if name else None
                slug = re.sub(r'[^\w\s-]', '', slug) if slug else None
                
                summary_element = hun.find('div', class_='woocommerce-product-details__short-description')
                summary = summary_element.decode_contents().strip() if summary_element else None
                
                sku = hun.find('span', class_='sku').text.strip() if hun.find('span', class_='sku') else None
                
                categories_element = hun.find('span', class_='posted_in')
                tags = [a.text for a in categories_element.find_all('a')] if categories_element else None
                
                description_html = None
                
                description_tab = hun.find('li', class_='description_tab')
                if description_tab:
                    description_content = description_tab.find_next('div', class_='woocommerce-Tabs-panel')
                    description_html = description_content.decode_contents() if description_content else None
                
                additional_info_tab = hun.find('li', class_='additional_information_tab')
                if additional_info_tab:
                    additional_info_content = additional_info_tab.find_next('div', class_='woocommerce-Tabs-panel').decode_contents()
                    additional_info_soup = BeautifulSoup(additional_info_content, 'html.parser')
                    attribute_elements = additional_info_soup.find_all('tr', class_='woocommerce-product-attributes-item')

                    attributes = {}
                    for attribute_element in attribute_elements:
                        attribute_label = attribute_element.find('th', class_='woocommerce-product-attributes-item__label').text.strip()
                        attribute_value = attribute_element.find('td', class_='woocommerce-product-attributes-item__value').text.strip()
                        attributes[attribute_label] = attribute_value

                    attribute = attributes.get("Attribute", "")
                    attribute_data = attributes.get("Attribute Data", "")
                    attribute_default = attributes.get("Attribute Default", "")
                else:
                    attribute = ""
                    attribute_data = ""
                    attribute_default = ""

                image_div = hun.find('div', class_='woocommerce-product-gallery')
                image_tags = image_div.find_all('img') if image_div else None
                
                featured_image = image_tags[0]['src'] if image_tags else None
                gallery_images = [img['src'] for img in image_tags[1:]] if len(image_tags) > 1 else None
                
                featured_images = f"{featured_image} ! alt : {name} ! title : {name}.jpg ! desc : {name} ! caption : {' | '.join(gallery_images) if gallery_images is not None else ''}" if featured_image else None
                
                breadcrumb_nav = hun.find('nav', class_='woocommerce-breadcrumb')
                last_a_tag = breadcrumb_nav.find_all('a')[-1] if breadcrumb_nav else None
                category = last_a_tag.text.strip() if last_a_tag else None
                
                # Store the data
                self.data.append({
                    'Price': price,
                    'Name': name,
                    'Slug': slug,
                    'Summary': summary,
                    'SKU': sku,
                    'Tags': tags,
                    'Description_HTML': description_html,
                    'Attribute': attribute,
                    'Attribute_Data': attribute_data,
                    'Attribute_Default': attribute_default,
                    'Featured_Images': featured_images,
                    'Category': category
                })
            except Exception as e:
                print(f"Error: {e}")

    def save_data_to_csv_and_print(self):
        # Specify the file name for the CSV file
        csv_file_name = 'rcfminibikes.csv'

        # Get the absolute path of the current working directory
        current_dir = os.getcwd()

        # Get the absolute path of the CSV file based on the current working directory
        csv_file_path = os.path.join(current_dir, csv_file_name)

        # Write the product data to a CSV file
        with open(csv_file_path, 'w', encoding='utf8', newline='') as f:
            # Check if the data list is not empty
            if self.data:
                fc = csv.DictWriter(f, fieldnames=self.data[0].keys())
                fc.writeheader()
                
                print('Now writing data to CSV file...')

                # Use tqdm to track the progress of writing
                progress_bar = tqdm(total=len(self.data), desc='Writing CSV')

                for row in self.data:
                    fc.writerow(row)
                    progress_bar.update(1)

                # Close the tqdm progress bar
                progress_bar.close()
            else:
                print('No data available. CSV file not created.')

        # Open the CSV file after writing is done
        try:
            if os.name == 'nt':  # Check if the system is Windows
                os.startfile(csv_file_path)
            elif os.name == 'posix':  # Check if the system is macOS or Linux
                subprocess.call(['xdg-open', csv_file_path])
            else:
                print('Unable to open the CSV file. Please open it manually.')
        except:
            print('Unable to open the CSV file. Please open it manually.')

        # Create a DataFrame from the product data
        df = pd.DataFrame(self.data)

        # Print the DataFrame
        print(df)

if __name__ == '__main__':
    base_url = "https://cheapkittens.com/shop/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    scraper = EScraperPRO(base_url, headers)
    total_pages = scraper.get_total_products()
    scraper.scrape_product_links(total_pages)
    scraper.scrape_product_data()
    scraper.save_data_to_csv_and_print()
