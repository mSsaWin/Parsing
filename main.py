from bs4 import BeautifulSoup as bs
import requests as req
from requests.exceptions import HTTPError
import re 
import pandas as pd
from copy import deepcopy


def findInfoOnPage(html):
    items = []
    objects = html.findAll("div",{"data-marker":"item","class":"iva-item-root-G3n7v photo-slider-slider-3tEix iva-item-list-2_PpT items-item-1Hoqq items-listItem-11orH js-catalog-item-enum","itemtype":"http://schema.org/Product"})
    for row in objects:
        name = row.findAll("a",{"target":"_blank","rel":"noopener","data-marker":"item-title"})
        price = row.findAll("span",{"class":"price-text-1HrJ_ text-text-1PdBw text-size-s-1PUdo"})
        data = row.findAll("div",{"class":"date-text-2jSvU text-text-1PdBw text-size-s-1PUdo text-color-noaccent-bzEdI","data-marker":"item-date"})

        if re.match(r"(?i)(видеокарт[аы]|RTX|GTX|AMD)", name[0].text) is not None and re.match(r"(\d+\s*\d*)", price[0].text) is not None and data:
            items.append([row["data-item-id"],name[0].text, re.findall(r"(\d+\s*\d*)", price[0].text), data[0].text])
    return items

def priceFilter(items, rang):
    new_items = []
    new_page = []

    for page in items:
        for item in page:
            if int(item[2][0].replace(' ', ''))>=rang[0] and int(item[2][0].replace(' ', ''))<=rang[1]:
                new_page.append(item)

        new_items.append(deepcopy(new_page))
        new_page.clear()

    return new_items
    


def printItems(items):
    output_dict = dict()
    id = []
    name = []
    price = []
    data = []
    for page in items:
        for item in page:
            id.append(item[0])
            name.append(item[1])
            price.append(f"{item[2][0]} RUB")
            data.append(item[3])

    output_dict["ID"] = id
    output_dict["NAME"] = name
    output_dict["PRICE"] = price
    output_dict["DATA"] = data

    frame = pd.DataFrame(output_dict)
    
    print(frame.to_string())
    
    writeCSV(frame)


def writeCSV(frame):
    filename = "graphics cards[30k-150k].csv"
    frame.to_csv(filename, encoding='cp1251', index = False)

rang = [30000, 150000]
all_items = []

url = "https://www.avito.ru/belgorod/tovary_dlya_kompyutera/komplektuyuschie/videokarty-ASgBAgICAkTGB~pm7gmmZw?p=1"
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

try:
    rsp = req.get(url,user_agent)
    rsp.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

soup = bs(rsp.text, "html.parser")

while "pagination-item-1WyVp pagination-item_arrow-Sd9ID pagination-item_readonly-2V7oG" not in str(soup.find("span",{"data-marker":"pagination-button/next"})):
    rsp = req.get(url,user_agent)
    soup = bs(rsp.text, "html.parser")
   
    all_items.append(findInfoOnPage(soup))

    url = f"{url[:len(url)-1]}{str(int(url[len(url)-1])+1)}"


all_items = priceFilter(all_items, rang)
printItems(all_items)
