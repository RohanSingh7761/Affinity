import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random

def get_listings():
    url = "https://m.olx.in/items/q-car-cover"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}: Fetching {url}")
            time.sleep(random.uniform(2, 5))
            
            r = requests.get(url, headers=headers, timeout=30)
            print(f"Status code: {r.status_code}")
            
            if r.status_code != 200:
                print(f"Bad response: {r.status_code}")
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            listings = []
            
            items = soup.find_all('div', {'data-aut-id': 'itemBox'})
            print(f"Found {len(items)} items with itemBox")
            
            if not items:
                items = soup.find_all('div', class_=lambda x: x and 'listing' in str(x).lower())
                print(f"Backup search found {len(items)} items")
                
            if not items:
                items = soup.find_all('div', class_=lambda x: x and any(word in str(x).lower() for word in ['item', 'card', 'product']))
                print(f"Generic search found {len(items)} items")
            
            for item in items:
                data = {}
                
                title = item.find('span', {'data-aut-id': 'itemTitle'})
                data['title'] = title.text.strip() if title else 'No title'
                
                price = item.find('span', {'data-aut-id': 'itemPrice'})
                data['price'] = price.text.strip() if price else 'Price not mentioned'
                
                loc = item.find('span', {'data-aut-id': 'item-location'})
                data['location'] = loc.text.strip() if loc else 'Location not specified'
                
                when = item.find('span', {'data-aut-id': 'item-date'})  
                data['posted'] = when.text.strip() if when else 'Date unknown'
                
                link = item.find('a')
                if link and link.get('href'):
                    data['url'] = 'https://www.olx.in' + link['href']
                else:
                    data['url'] = 'No link found'
                
                listings.append(data)
            
            return listings
            
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < 2:
                print("Retrying...")
                continue
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1}")
            if attempt < 2:
                print("Retrying...")
                continue
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < 2:
                print("Retrying...")
                continue
    
    print("All attempts failed")
    return []

def save_to_file(data):
    with open('olx_car_covers.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    if data:
        with open('olx_car_covers.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'price', 'location', 'posted', 'url'])
            writer.writeheader()
            writer.writerows(data)

print("Getting car cover listings from OLX...")

listings = get_listings()

if listings:
    print(f"Found {len(listings)} listings")
    save_to_file(listings)
    print("Saved to olx_car_covers.json and olx_car_covers.csv")
    
    print("\nFirst few results:")
    for i, item in enumerate(listings[:3]):
        print(f"\n{i+1}. {item['title']}")
        print(f"   Price: {item['price']}")
        print(f"   Location: {item['location']}")
        print(f"   Posted: {item['posted']}")
else:
    print("No listings found or error occurred")