import requests
import asyncio
import aiohttp
import time
import json

os.environ.setdefault('AIOHTTP_NO_EXTENSIONS', '1')

base_url='https://collectionapi.metmuseum.org/public/collection/v1/objects'
resp = requests.get(url=base_url)
print (resp)
object_ids_list = resp.json()["objectIDs"]
print(len(object_ids_list))

object_url_list = [f"{base_url}/{s}" for s in object_ids_list]
short_list = object_url_list[-2:]
short_list

async def get(url, session):
  try:
    async with session.get(url=url, headers={
        'User-Agent': 'PostmanRuntime/7.26.8',
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate"
    }) as response:
      resp = await response.read()
      print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
      return await response.json()
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


        

start = time.time()
# await main(object_url_list)
# loop = asyncio.get_event_loop()
# data = asyncio.run_coroutine_threadsafe(main(short_list), loop).result()
# end = time.time()

start = time.time()
data = asyncio.run(main(object_url_list))
end = time.time()

print("Took {} seconds to pull {} websites.".format(end - start, len(data)))
print(type(data[0]))
print(data)

data_with_image_links = [d for d in data if d['primaryImage']]
print(data_with_image_links)
