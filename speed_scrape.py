import re
from time import sleep
from turtle import right
from requests import request
from bs4 import BeautifulSoup, SoupStrainer
import requests

from pandas_json import DataFrameOutput


"""
<a href="https://www.silverlinetrailerspottstown.com/inventory/2024-southern-utility-trailers-7x14-14k-dump-trailer-trd-high-side-trd-5625/">
					<div class="right-button">
						<i class="fas fa-tasks"></i>
						<p> View Details</p>
					</div>
				</a>"""


def get_info(url, session):
    response = session.get(
        url=url,
        headers=headers,
    )

    bs = BeautifulSoup(response.text, "html.parser")

    # <div class="single-info single-info-visible">
    info_div = bs.find("div", class_="inventory-single-details")
    info_dict = {}

    # Get all the 'single-info-desc-name' and 'single-info-values' elements
    desc_names = info_div.find_all("div", class_="single-info-desc-name")
    values = info_div.find_all("div", class_="single-info-values")

    # Iterate over the pairs and store them in the dictionary
    for name, value in zip(desc_names, values):
        key = name.get_text(strip=True)
        val = value.get_text(strip=True)
        info_dict[key] = val
    # Output the dictionary
    return info_dict


def contents(tag):
    return tag.hasattr("href") and tag.hasattr("class") and tag["class"] == "right"


if __name__ == "__main__":
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    info_lists = []
    # /pg=number
    pg = 1
    while True:
        response = s.get(
            url=f"https://www.silverlinetrailer.com/inventory/?pg={pg}",
            headers=headers,
        )
        filter = SoupStrainer("div", id="wpp-manage-inventory-list-main-container")
        bs = BeautifulSoup(response.text, "html.parser", parse_only=filter)
        inventory_link = re.compile("https://www.silverlinetrailer.com/inventory/")
        # <div class="wpp-manage-inventory-container inventory-item-basic">
        container = bs.find("div", id="wpp-manage-inventory-list-main-container")
        items = bs.find_all(
            "div",
            class_="wpp-manage-inventory-container list-view inventory-item-basic",
        )
        for item in items:
            # <div id="inventory-right-buttons">
            right = item.find("div", class_="inventory-right-buttons")

            link = right.find(href=inventory_link)

            info_lists.append(get_info(link["href"], s))
        pg_container = bs.find("div", class_="pagination-controls-container")
        if (
            pg_container.find("a", class_="page-right-button disable-page-button ")
            is not None
        ):
            break
        pg += 1
        print(pg)
    data = DataFrameOutput(data=info_lists)
    print(data.dataframe)
    data.dataframe.to_csv("test2.csv", index=False)
