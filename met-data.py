import os
from os import path
import requests
import asyncio
import aiohttp
import time
import json
import random
import urllib.request
from bs4 import BeautifulSoup as BS
import numpy as np

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/15.4 Safari/605.1.15"}

base_url='https://collectionapi.metmuseum.org/public/collection/v1/objects'
resp = requests.get(url=base_url)
print (f"Met site status code: {resp.status_code}")
object_ids_list = resp.json()["objectIDs"]

object_url_list = [f"{base_url}/{s}" for s in object_ids_list]
object_url_list = object_url_list[:10000]
num_artworks = len(object_url_list)
print(f"Number of artworks: {num_artworks}")
num_chucks = num_artworks/2000
splits = np.array_split(object_url_list, num_chucks)
short_list = random.sample(object_url_list,10)

async def get(url, session):
  try:
    async with session.get(url=url, headers=headers) as response:
      resp = await response.read()
      print("Successful response from url {} with length {}.".format(url, len(resp)))
      return await response
  except Exception as e:
    print("Unable to get url {} due to {}.".format(url, e.__class__))
    print(e)
    

async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])
        return ret
    
def get_objects_sync(urls):
    data = []
    for object_id in range(0, len(urls)):
        object_url = f'{base_url}/{object_id}'
        art_object = requests.get(url=object_url)
        data.append(art_object)
    return data

def extract_images(data_with_link, headers):
    for obj in data_with_link:
        obj_id = obj['objectID']
        page_link = obj['objectURL']
        print(f"Link to object: {page_link}")
        page = requests.get(page_link, headers=headers)
        print(f"Got page, len: {len(page.content)}")
        
        # instead save to s3 bucket

def extract_image(page, object_id):
    soup = BS(page.content, features="html.parser")
    images = soup.findAll('img', {'id':'artwork__image'})
    print(f"Images found in page: {len(images)}")
    for image in images:
        img_src = image['src']
        alt_text = image['alt']
        print(f"Image desc: {alt_text}")
        print(f"Image src: {img_src}")
        extension = os.path.splitext(img_src)[1]
        if not extension:
            extension = "jpeg"
        local_file = f"img/{object_id}.{extension}"
        urllib.request.urlretrieve(img_src, local_file)
        obj["localLink"] = local_file

for index, chunk in enumerate(splits):
    print(f"Starting chunk {index} of {len(splits)}")
    start = time.time()
    response_data = asyncio.run(main(chunk))
    json_data = [response.json() for response in response_data]
    data_with_link = [d for d in json_data if d['objectURL']]
    print(f"Artwork with link: {len(data_with_link)}")

    object_links = [d['objectURL'] for d in data_with_link]
    object_pages = asyncio.run(main(object_links))
    page_contents = [page.content for page in object_pages]
    extract_images(data_with_link, headers)
    end = time.time()
    time.sleep(2)

print("Took {} seconds to pull {} websites.".format(end - start, len(num_artworks)))

# data_with_link = [d for d in data if d['objectURL']]

print("Images retrieved")

