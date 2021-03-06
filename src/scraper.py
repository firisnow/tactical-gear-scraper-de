import requests
import time
import json
import logging

from requests_html import HTMLSession
from bs4 import BeautifulSoup

from product_listings.trauma_kit_listings import trauma_kit_url_list
from product_listings.tourniquet_listings import tourniquet_url_list
from product_listings.swat_tourniquet_listings import swat_tourniquet_url_list
from product_listings.em_bandages_listings import em_bandages_url_list
from product_listings.hem_dressing_listings import hem_dressing_url_list
from product_listings.hemostatic_agent_listings import hemostatic_agent_url_list
from product_listings.occlusive_dressing_listings import occ_dressing_url_list

session = HTMLSession()

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

prefetched_data_to_serialize = {
    'scheme': ['product name', 'price in €', 'items available (if info on website)', 'url']
}


test_list = [
    "https://www.nltactical.nl/en/sam-chito-sam-z-fold-6.html",
    "https://www.nltactical.nl/en/soffe-t-shirt-black-3-pack.html"
]


def handle_nltactical_listing(soup):
    # <span class="hurry too-late"><i class="icon-negative"></i> Out of stock</span>
    for tag in soup.find_all(class_="too-late"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all("div", class_="for"):
        price = tag.get_text().split('In stock')[0].strip()[1:].strip()
        if ",-" in price:
            price = price.split(',-')[0]
        break
    return name, price, None


def handle_adventurestore_listing(soup):
    # <div id="product-availability" class="js-product-availability product-unavailable mar_b6 fs_md"> Nicht auf Lager</div>
    for tag in soup.find_all(class_="product-unavailable"):
        if "Nicht auf Lager" in tag.get_text():
            return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all("span", class_="price"):
        price = tag["content"]
        break
    return name, price, None


def handle_medicbravo_listing(soup):
    for tag in soup.find_all(class_="status-0"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all("div", class_="price"):
        price = tag.contents[1].get_text().strip()[:-1].strip()
        break
    return name, price, None


def handle_emtshop_shop_listing(soup):
    for tag in soup.find_all(class_="out-of-stock"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all("div", class_="price"):
        price = tag.get_text().split('Incl. tax')[0].strip()[1:]
        break
    return name, price, None


def handle_tactical_equipements_fr_listing(soup):
    for tag in soup.find_all(class_="product-unavailable"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all('span', itemprop="price"):
        price = tag["content"]
        break
    return name, price, None


def handle_meetb_listing(soup):
    versand = False
    for tag in soup.find_all(class_="fv-style-detail"):
        if "sofort verfügbar" in tag.get_text():
            versand = True

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all('meta', itemprop="price"):
        price = tag["content"]
        break
    return name, price, None


def handle_lsinnoventa_listing(soup):
    for tag in soup.find_all(class_="out-of-stock"):
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all('span', class_="price"):
        price = tag.get_text()[1:].strip()
        break
    return name, price, None


def handle_bhvtotaal_listing(soup):
    for tag in soup.find_all(class_="outofstock"):
        return None, None, None

    for tag in soup.find_all(itemprop="name"):
        if tag['data-ui-id'] == "page-title-wrapper":
            name = tag.string.strip()
            break
    for tag in soup.find_all('span', class_="price"):
        price = tag.string.strip()[2:]
        break
    return name, price, None


def handle_helpishop_listing(soup):
    versand = False
    for tag in soup.find_all(src="images/ampelgreen.png"):
        if "lieferbar in 3-5 Werktagen" in tag['title']:
            versand = True
    for tag in soup.find_all(src="images/ampelyellow.png"):
        if "lieferbar in 3-5 Werktagen" in tag['title']:
            versand = True
    if not versand:
        return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all('td', class_="art_preis_detail_wert"):
        price = tag.get_text()[:-2].strip()
        break
    return name, price, None


def handle_sanismart_listing(soup):
    for tag in soup.find_all(class_="twt-product-stock-label"):
        if "Derzeit nicht auf Lager." in tag.get_text():
            return None, None, None

    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="product-detail-price-container"):
        price = tag.contents[1]['content']
        break
    return name, price, None


def handle_huntac_listing(soup):
    versand = False
    for tag in soup.find_all(class_="delivery--status-available"):
        versand = True

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all(itemprop="price"):
        price = tag['content']
        break
    return name, price, None


def handle_ostalb_med_listing(soup):
    versand = False
    for tag in soup.find_all(src="images/icons/status/orange.png"):
        versand = True
    for tag in soup.find_all(src="images/icons/status/green.png"):
        versand = True

    if not versand:
        return None, None, None
    name = soup.h1.string.strip()
    for tag in soup.find_all(class_="current-price-container"):
        price = tag.string.split(' ')[0].strip()
        break
    return name, price, None


def handle_medididakt_listing(soup):
    for tag in soup.find_all(class_="out-of-stock"):
        return None, None, None

    name = soup.h1.string.strip()
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
        if "UVP" in price:
            price = tag_p.contents[3].split('Nur')[1]\
                .split('EUR')[0].strip()
            print(price)
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
        #print(t)

        try:
            if not ("mbs-medizintechnik.com" in t or "lsinnoventa" in t):
                #website down, don't ship to de
                if "fenomed" in t or "helpishop" in t or \
                        "bhvtotaal" in t:
                    r = session.get(t)
                    r.html.render(timeout=20)
                    soup = BeautifulSoup(r.html.html, features="html.parser")
                else:
                    r = requests.get(t)
                    soup = BeautifulSoup(r.content, features="html.parser")
            else:
                soup = None
        except:
            soup = None

        try:
            logging.info('Processing', t)
            if soup is None:
                l = [None]
            elif 'medic-bandages' in t:
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
                l = handle_fenomed_listing(soup)
            elif "medididakt" in t:
                l = handle_medididakt_listing(soup)
            elif "ostalb-med-shop" in t:
                l = handle_ostalb_med_listing(soup)
            elif "huntac" in t:
                l = handle_huntac_listing(soup)
            elif "sanismart" in t:
                l = handle_sanismart_listing(soup)
            elif "helpishop" in t:
                l = handle_helpishop_listing(soup)
            elif "bhvtotaal" in t:
                l = handle_bhvtotaal_listing(soup)
            elif "lsinnoventa" in t:
                l = handle_lsinnoventa_listing(soup)
            elif "meetb" in t:
                l = handle_meetb_listing(soup)
            elif "tactical-equipements.fr" in t:
                l = handle_tactical_equipements_fr_listing(soup)
            elif "emtshop" in t:
                l = handle_emtshop_shop_listing(soup)
            #elif "medicbravoshop" in t: # prices rise so much wtf?
            #    l = handle_medicbravo_listing(soup)
            elif "adventurestore" in t:
                l = handle_adventurestore_listing(soup)
            elif "nltactical" in t:
                l = handle_nltactical_listing(soup)
            else:
                l = [None]
        except:
            l = [None]

        if l[0] is not None:
            if "€" in l[1] or "E" in l[1]:
                print("Could not convert price:", t)
            else:
                l_res.append((*l, t))
        
        if len(l_res) >=10:
            break
    
   
    l_res = sorted(l_res, key=lambda tup: float(tup[1].replace(',', '.')))
    for l in l_res:
        result = result + "\n\n" + format_listing(link=l[3], name=l[0],
                                                price=l[1], lager=l[2])
    prefetched_data_to_serialize[name] = l_res
    return result


def fetch_data():
    for key in name_list_dict:
        prefetched_data[key] = handle_list(name=key,
                                           url_list=name_list_dict[key])
    prefetched_data_to_serialize['time'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                         time.gmtime())
    try:
        with open('/src/output/tacmed_data.json', 'w', encoding='utf-8') as f:
            json.dump(prefetched_data_to_serialize, f, ensure_ascii=False, indent=4)
    except:
        logging.error('Could not dump prefetched data')


def fetch_data_runner():
    print('data fetcher running')
    while True:
        fetch_data()
        time.sleep(300)
#fetch_data()
#print(handle_list('Test', test_list))
