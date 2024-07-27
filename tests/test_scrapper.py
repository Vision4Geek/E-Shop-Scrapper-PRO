import pytest

from bs4 import BeautifulSoup
from escrapper.scrapping_parser import ParsePage

def test_dummy():
    # this is a dummy test data
    parser = ParsePage(html_soup=BeautifulSoup())
    assert type(parser) == ParsePage

    # Print the results
    print("Parser instance created successfully:", parser)
