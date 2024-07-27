import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_product_info(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            # Try finding product title with <h1> tag first
            product_title = soup.find('h1', class_='product_title')
            if product_title:
                product_title = product_title.text.strip()
            else:
                # If <h1> tag not found, try with <h2> tag
                product_title = soup.find('h2', class_='product_title')
                if product_title:
                    product_title = product_title.text.strip()
                else:
                    product_title = "Title not found"
            price = soup.find('p', class_='price').text.strip()
            product_description = soup.find('div', class_='woocommerce-Tabs-panel')
            if product_description:
                # Remove only the first <h2> tag from description
                first_h2_tag = product_description.find('h2')
                if first_h2_tag:
                    first_h2_tag.decompose()
                product_description = product_description.decode_contents()
            else:
                product_description = None
            return {
                'title': product_title,
                'price': price,
                'description': product_description
            }

async def main():
    url = 'https://cheappuppiesforsale.com/product/boston-terrier-puppy-for-sale/'
    product_info = await fetch_product_info(url)
    print(product_info)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
