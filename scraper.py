import requests
import time

from requests_html import HTMLSession
from bs4 import BeautifulSoup

from scraper_utils import get_name_from_h1

from product_listings.trauma_kit_listings import trauma_kit_url_list
from product_listings.tourniquet_listings import tourniquet_url_list
from product_listings.swat_tourniquet_listings import swat_tourniquet_url_list
from product_listings.em_bandages_listings import em_bandages_url_list
from product_listings.hem_dressing_listings import hem_dressing_url_list
from product_listings.hemostatic_agent_listings import hemostatic_agent_url_list
from product_listings.occlusive_dressing_listings import occ_dressing_url_list


name_list_dict = {
    'CAT / SOF / SAM Tourniquet': tourniquet_url_list,
    'SWAT Tourniquet': swat_tourniquet_url_list,
    'Emergency Bandages': em_bandages_url_list,
    'Hemostatic Dressing (QuikClot, Celox, HemCon, ChitoSam)':
        hem_dressing_url_list,
    'Hemostatic Agents (Granules)': hemostatic_agent_url_list,
    'Chest Seal': occ_dressing_url_list,
}

prefetched_data = dict()


test_list = [
    "https://www.medididakt.de/shop/notfallequipment-notfallbehaeltnisse-notfallsets/sonstiges-notfallequipment-notfallbehaeltnisse-notfallsets/emergency-bandage-notfall-bandage-t3/",
    "https://www.medididakt.de/shop/notfallkoffer-taschen/notfalltaschen/taktische-tasche-medical-bag-gefuellt/"
    ]


def handle_medididakt_listing(soup):
    for tag in soup.find_all(class_="out-of-stock"):
        return None, None, None

    name = get_name_from_h1(soup)
    for tag in soup.find_all(class_="woocommerce-Price-amount"):
        price = tag.contents[0].string.strip()
        break
    return name, price, None


def handle_fenomed_listing(soup):
    versand = False
    for tag in soup.find_all('div', class_="availability_1"):
        versand = True
    for tag in soup.find_all('div', class_="availability_2"):
        versand = True

    if not versand:
        return None, None, None
    name = soup.h1.contents[0].string.strip()
    for tag in soup.find_all(class_="price-gross-net"):
        price = tag.contents[0].contents[0].string.strip()[:-2]
        break
    return name, price, None


def handle_bestprotection_listing(soup):
    for tag in soup.find_all(class_="delivery--text-not-available"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(itemprop="price"):
        price = tag['content']
        break
    return name, price, None


def handle_1a_med_listing(soup):
    versand = False
    for tag in soup.find_all(class_="delivery-information--available"):
        versand = True

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="sm-buying-box__price-tax"):
        price = tag.get_text().strip().split(' ')[0].strip()[:-2]
        break
    return name, price, None


def handle_warthog_listing(soup):
    for tag in soup.find_all(class_="label-danger"):
        if "Nicht mehr lieferbar" in tag.get_text():
            return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(id="our_price_display"):
        price = tag.get_text()
        break
    return name, price, None


def handle_flexeo_listing(soup):
    for tag in soup.find_all(class_="out-of-stock"):
        return None, None, None
    for tag in soup.find_all(class_="available-on-backorder"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="woocommerce-Price-amount"):
        price = tag.get_text()[:-2]
        break
    return name, price, None


def handle_mbs_medizintechnik_listing(soup):
    for tag in soup.find_all(class_="alert--content"):
        if 'Dieser Artikel steht derzeit nicht zur Verfügung!' in tag.get_text():
            return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="gross-amount"):
        price = tag.get_text().split(' ')[1].split('€')[0].strip()
        break
    return name, price, None


def handle_verbandskasten_listing(soup):
    versand = False
    for tag in soup.find_all(class_="in-stock"):
        versand = True

    if not versand:
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="woocommerce-Price-currencySymbol"):
        price = tag.next_sibling.get_text().strip()
        break
    return name, price, None


def handle_obramo_security_listing(soup):
    # check if available
    for tag in soup.find_all(class_="status"):
        if "status-0" in tag['class']:
            return None, None, None
    for tag in soup.find_all(class_="coming_soon"):
            return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="font-price"):
        price = tag.get_text().split('€')[0].strip()
        break
    return name, price, None


def handle_md_textil_listing(soup):
    # check if available
    versand = False
    lager = None
    for tag in soup.find_all(class_="fa-truck"):
        if "sofort verfügbar" in tag.next_sibling.get_text():
            versand = True
        elif "Stück auf Lager" in tag.next_sibling.get_text():
            versand = True
            lager = tag.next_sibling.get_text().split('Stück auf Lager')[0].strip()

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="price"):
        price = tag.get_text().split('€')[0].strip()
        break
    return name, price, lager


def handle_wero_listing(soup):
    # check if available
    versand = False
    for tag in soup.find_all(class_="delivery--status-available"):
        versand = True
    for tag in soup.find_all(class_="alert--content"):
        if "Dieser Artikel steht derzeit nicht zur Verfügung!" in tag.get_text():
            versand = False

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="price--content"):
        price = tag.get_text().split('€')[0].strip()
        break
    return name, price, None


def handle_medic_bandages_listing(soup):
    # check if available
    for tag in soup.find_all(class_="img-shipping-time"):
        if not tag.img['src'] in ['images/icons/status/orange.png',
                              'images/icons/status/green.png']:
            return None, None, None

    name = soup.h1.string
    for tag_p in soup.find_all(class_="current-price-container"):
        price = tag_p.get_text().split('EUR')[0].strip()
        break
    lager = None
    for tag_q in soup.find_all(class_="products-quantity-value"):
        lager = tag_q.string.strip()

    return name, price, lager


def format_listing(link, name, price, lager):
    t = ""+name+": " + price + " €"
    if lager is not None:
        t = t + " ("+lager+" available)"
    t = t +"\nLink: " + link
    return t


def handle_list(name, url_list):
    result = ""
    l_res = list()
    for t in url_list:
        r = requests.get(t)
        soup = BeautifulSoup(r.content, features="html.parser")

        if 'medic-bandages' in t:
            l = handle_medic_bandages_listing(soup)
        elif 'wero-med-x' in t:
            l = handle_wero_listing(soup)
        elif "md-textil.info" in t:
            l = handle_md_textil_listing(soup)
        elif "obramo-security" in t:
            l = handle_obramo_security_listing(soup)
        elif "der-verbandskasten.de" in t:
            l = handle_verbandskasten_listing(soup)
        elif "mbs-medizintechnik.com" in t:
            l = handle_mbs_medizintechnik_listing(soup)
        elif "warthog-store" in t:
            l = handle_warthog_listing(soup)
        elif "flexeo" in t:
            l = handle_flexeo_listing(soup)
        elif "1a-medizintechnik" in t:
            l = handle_1a_med_listing(soup)
        elif "bestprotection.de" in t:
            l = handle_bestprotection_listing(soup)
        elif "fenomed" in t:
            session = HTMLSession()
            r = session.get(t)
            r.html.render()
            soup = BeautifulSoup(r.html.html, features="html.parser")
            l = handle_fenomed_listing(soup)
        elif "medididakt" in t:
            l = handle_medididakt_listing(soup)
        else:
            l = [None]

        if l[0] is not None:
            l_res.append((*l, t))

    l_res = sorted(l_res, key=lambda tup: float(tup[1].replace(',', '.')))
    for l in l_res:
        result = result + "\n\n" + format_listing(link=l[3], name=l[0],
                                                price=l[1], lager=l[2])
    return result

#"""
result = ""
for key in name_list_dict:
    if result != "":
        result = result + "\n\n"
    result = result + handle_list(name=key, url_list=name_list_dict[key])
print(result)
#"""
"""
print(handle_list('Test', test_list))
"""
def fetch_data():
    for key in name_list_dict:
        prefetched_data[key] = handle_list(name=key,
                                           url_list=name_list_dict[key])

def fetch_data_runner():
    print('data fetcher running')
    while True:
        fetch_data()
        time.sleep(600)
