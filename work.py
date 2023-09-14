import argparse
import os
import time
from pathlib import Path
import requests
import threading
import multiprocessing
import asyncio

image_urls = []
with open('images.txt', 'r') as images:
    for image in images.readlines():
        image_urls.append(image.strip())

image_path = Path('./images/')


def download_image(url):
    global image_path
    start_time = time.time()
    response = requests.get(url, stream=True)
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Downloaded {filename} in {end_time:.2f} seconds")


async def download_image_async(url):
    start_time = time.time()
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"stream": True})
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Downloaded {filename} in {end_time:.2f} seconds")


def download_images_threading(urls):
    start_time = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.time() - start_time
    print(f"Total time using threading: {end_time:.2f} seconds")


def download_images_multiprocessing(urls):
    start_time = time.time()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time() - start_time
    print(f"Total time using multiprocessing: {end_time:.2f} seconds")


async def download_images_asyncio(urls):
    start_time = time.time()
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download_image_async(url))
        tasks.append(task)

    await asyncio.gather(*tasks)

    end_time = time.time() - start_time
    print(f"Total time using asyncio: {end_time:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка изображения с URL-адресов и сохранение их на диск.")
    parser.add_argument("--urls", nargs="+", help="Список URL-адресов для загрузки изображений.")
    args = parser.parse_args()

    urls = args.urls
    if not urls:
        urls = image_urls

    print(f"Загрузка {len(urls)} с использованием модуля threading...")
    download_images_threading(urls)

    print(f"\nЗагрузка {len(urls)} с использованием модуля multiprocessing...")
    download_images_multiprocessing(urls)

    print(f"\nЗагрузка {len(urls)} с использованием модуля asyncio...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_images_asyncio(urls))