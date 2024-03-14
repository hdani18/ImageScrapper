import requests
from bs4 import BeautifulSoup
import validators
import uuid 
import os 
from django.conf import settings
from urllib.parse import urljoin
import time  
import threading

IMAGE_BASE_PATH = f"{settings.ASSETS_DIR}/images"

def is_valid_url(url_string: str) -> bool:
    return bool(validators.url(url_string.strip()))

def fetch_images(url: str) -> tuple[list[str], str]:
    lst_links = []
    error_message = ""
    start_time = time.time()

    r = requests.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        images = soup.find_all('img')
        threads = []

        for image in images:
            link = image.get('src')
            if link:
                if not is_valid_url(link):
                    link = urljoin(url, link)
                thread = threading.Thread(target=download_image_async, args=(link, lst_links))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()
    else:
        error_message = f"Failed to fetch URL: {url}. Status code: {r.status_code} {r.reason}"

    end_time = time.time()
    total_time = end_time - start_time

    print(f"Total time taken to download images: {total_time} seconds")

    return lst_links, error_message

def download_image_async(url: str, lst_links: list) -> None:
    try:
        file_ext = url.split(".")[-1]
        file_name = str(uuid.uuid4()) + "." + file_ext
        file_path = os.path.join(IMAGE_BASE_PATH, file_name)

        with open(file_path, 'wb') as f:
            response = requests.get(url)
            f.write(response.content)

        img_url = f"{settings.STATIC_URL}images/{file_name}"
        lst_links.append(img_url)
    except Exception as e:
        print(f"Error downloading image: {e}")
