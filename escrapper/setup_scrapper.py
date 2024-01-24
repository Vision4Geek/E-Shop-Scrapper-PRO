import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from tqdm import tqdm
import subprocess
from tabulate import tabulate
import re, os
import random
from datetime import datetime, timedelta
 
# Generate a random date and time
start_date = datetime(2022, 1, 1)
end_date = datetime.now()
random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

# Format the random date and time
formatted_date = random_date.strftime("%Y-%m-%d %H:%M:%S")

# Set the headers for the HTTP requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

# Initialize variables
productlinks = []  # List to store product links
data = []  # List to store product data
categories = []  # List to store categories
base_url = "https://rcfminibikes.com/product-category/all/page/"  # Base URL for the product pages

# Send a request to the first page to get the total number of products
response = requests.get(base_url + "1", headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
# Define the number of products displayed per page
products_per_page = 16 

# Find the pagination element in the HTML
pagination_info = soup.find('nav', class_='woocommerce-pagination')

if pagination_info:
    # Extract the page numbers from the pagination element
    page_numbers = pagination_info.find_all('a', class_='page-numbers')
    
    # Check if there are page numbers available
    if page_numbers:
        # Get the second-to-last page number (last page often represented by "next" link)
        last_page = int(page_numbers[-2].text)
    else:
        last_page = 0
        
    # Calculate the total number of products based on the last page number and products per page
    total_products = last_page * products_per_page
else:
    # If no pagination information is found, set total_products to 0
    total_products = 0

# Calculate the total number of pages

total_pages = (total_products - 1) // products_per_page + 1
# Loop through each page
for page in tqdm(range(1, total_pages + 1), desc='Scraping Pages'):
    url = base_url + str(page)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all product summaries on the current page
    product_list = soup.find_all('div', class_='wpbf-woo-loop-summary')

    # Extract the product links from the product summaries
    for product_summary in product_list:
        # Extract the post title from the <h3> tag
        post_title = product_summary.find('h3', class_='woocommerce-loop-product__title').text
       
        # Extract the href link from the <a> tag
        link = product_summary.find('a', class_='woocommerce-LoopProduct-link')['href']
        productlinks.append(link)

# Initialize a list to store product names
product_names = []
import csv

# Initialize the list to store product data
data = []

# Iterate through each product link
    # Create a dictionary to store the product data
    
    # Append the product data to the list
    data.append(product_data)

# Specify the file name for the CSV file
csv_file_name = 'rcfminibikes.csv'

# Get the absolute path of the current working directory
current_dir = os.getcwd()

# Get the absolute path of the CSV file based on the current working directory
csv_file_path = os.path.join(current_dir, csv_file_name)

# Write the product data to a CSV file
with open(csv_file_path, 'w', encoding='utf8', newline='') as f:
    # Check if the data list is not empty
    if data:
        fc = csv.DictWriter(f, fieldnames=data[0].keys())
        fc.writeheader()
        
        print('Now writing data to CVS file...')

        # Use tqdm to track the progress of writing
        progress_bar = tqdm(total=len(data), desc='Writing CSV')

        for row in data:
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
df = pd.DataFrame(data)

# Print the DataFrame
print(df)
