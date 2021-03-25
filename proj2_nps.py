#################################
##### Name: Yue Wang
##### Uniqname: wyjessic
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets  # file that contains your API key
#import requests_cache
CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}
class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    pass
    def __init__(self, category, name, address,zipcode,phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_dict = {}
    base_url = "https://www.nps.gov"
    cache_dict = open_cache()
    search_url = "https://www.nps.gov/index.htm"
    try:
        flag = False
        cache_dict[search_url]
    except:
        flag = True
        print('Fetching')
        response = requests.get(search_url)
        cache_dict[search_url] = response.text
        save_cache(cache_dict)
    if flag == False:
        print("Using cache")
    
    soup = BeautifulSoup(cache_dict[search_url], 'html.parser')
    state_list = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    state_listing_li =state_list.find_all('li', recursive=False)
    for i in state_listing_li:
        state_dict[i.text.lower()] = base_url + i.find('a',href=True)['href']
    return state_dict
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''

    cache_dict = open_cache()
    search_url = site_url
    try:
        flag = False
        cache_dict[search_url]
    except:
        flag = True
        print('Fetching')
        response = requests.get(search_url)
        cache_dict[search_url] = response.text
        save_cache(cache_dict)
    if flag == False:
        print("Using cache")
    
    park_soup = BeautifulSoup(cache_dict[search_url], 'html.parser')
    try:
        park_category = park_soup.find('span', class_ = "Hero-designation").text
    except:
        park_category = ""
    #park_name = park_soup.find('a', id = "anch_10",class_ = "Hero-title  -long").text
    park_name = park_soup.find('a',class_='Hero-title').text
    try:
        park_address = park_soup.find(class_ = "adr").find_all(
            'span')[1].span.text +", " + park_soup.find(class_ = "adr").find_all('span')[1].find(
                class_='region').text
        park_zipcode =  park_soup.find(class_ = "adr").find_all('span')[1].find(
                class_='postal-code').text.split()[0]
        

    except:
        park_address=""
        park_zipcode=""
    
    park_phone = park_soup.find('span',class_ = "tel").text.split('\n')[1]
    return NationalSite(park_category,park_name,park_address,park_zipcode,park_phone)



def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    site_list = []
    cache_dict = open_cache()
    search_url = state_url
    try:
        flag = False
        cache_dict[search_url]
    except:
        flag = True
        print('Fetching')
        response = requests.get(search_url)
        cache_dict[search_url] = response.text
        save_cache(cache_dict)
    if flag == False:
        print("Using cache")
    soup = BeautifulSoup( cache_dict[search_url], 'html.parser')
    park_list = soup.find( id='list_parks').find_all('h3')

    for park in park_list:
        park_href = park.find('a')['href']
        site_list.append(get_site_instance(f'https://www.nps.gov{park_href}index.htm'))
    return site_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    cache_dict = open_cache()
    search_url = "http://www.mapquestapi.com/search/v2/radius"
    try:
        flag = False
        cache_dict[search_url]
    except:
        flag = True
        param = {"key": secrets.API_KEY,
            "origin": site_object.zipcode,
            "radius":10,
            "maxMatches":10,
            "ambiguities":"ignore",
            "outFormat":"json"}
        print('Fetching')
        response = requests.get(search_url,params=param)
        cache_dict[search_url] = response.json()
        save_cache(cache_dict)
    if flag == False:
        print("Using cache")
    
    res_json = cache_dict[search_url]
    return res_json

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()     

if __name__ == "__main__":
    
    
    #requests_cache.install_cache('demo_cache')
    
    state_list = build_state_url_dict()
    while True:
        state_name = input('Enter a state name (e.g. Michigan, michigan) or "exit"\n:').lower()
        if state_name == 'exit':
            exit()
        try:
            state_url = state_list[state_name]
        except:
            print("[error] Enter proper state name")
            continue
        site_list = get_sites_for_state(state_url)
        print('----------------------------------')
        print(f'List of national sites in {state_name}')
        print('----------------------------------')
        leng_site = len(site_list)
        for i in site_list:
            print(f'[{site_list.index(i)+1}]',i.info())
        while True:
            state_num = input('Choose the number for detail search or "exit" or "back"\n:')
            if state_num == 'back':
                break
            if state_name == 'exit':
                exit()
            try:
                state_num = int(state_num)
            except:
                print("[Error] Invalid input")
                continue
            if leng_site > leng_site or leng_site <=0 :
                print("[Error] Invalid input")
                continue

            state_num = int(state_num)-1
            res_json = get_nearby_places(site_list[state_num])
            print('----------------------------------')
            print(f'Place near {site_list[state_num].name}')
            print('----------------------------------')
            for i in res_json['searchResults']:
                try:
                    category = i['fields']["group_sic_code_name"]
                except: category = "no category"
                try:
                    address = i['fields']["address"]
                except: address = "no address"
                try:
                    city = i['fields']["city"]
                except:
                    city = "no city"
                if  category  =='': category = "no category"
                if  address  =='': address = "no address"
                if  city  =='': city = "no city"
                print(f'- {i["name"]} ({category}): {address}, {city}')
            

        





