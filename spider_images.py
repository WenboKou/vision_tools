import os
import re
import time
import threading

import requests
from threading import *
import argparse
import json
from tqdm import tqdm


all_image_urls = []
num_images = 0


def download(img_save_path, image_urls, thread_name):
    global num_images
    cnt = 0
    for image_url in image_urls:
        try:
            if image_url is not None:
                image = requests.get(image_url, timeout=7)
            else:
                continue
        except BaseException:
            print('can not download this image from %s' % image_url)
            continue
        else:
            string = os.path.join(img_save_path, '%d_%d.png' % (thread_name, cnt + 1))
            fp = open(string, 'wb')
            fp.write(image.content)
            fp.close()
            cnt += 1
    num_images += cnt


def collect_image_url(url):
    try:
        Result = requests.get(url, timeout=7)
    except BaseException:
        return False, None
    else:
        result = Result.text
        img_urls = re.findall('https://st.*?jpg', result)
        if len(img_urls) == 0:
            return False, None

        return True, img_urls


def remove_repeated_url():
    visited_images = set()
    image_urls = []
    for image_url in all_image_urls:
        image_name = image_url.split('/')[-1]
        if image_name in visited_images:
            continue
        visited_images.add(image_name)
        image_urls.append(image_url)
    print(f'{len(all_image_urls)} image urls in total.')
    print(f'removing {len(all_image_urls) - len(image_urls)} repeated urls, {len(image_urls)} stays.')
    return image_urls


def spider_images(raw_url, page_start, page_end):
    global all_image_urls
    image_urls = []
    for page_idx in range(page_start, page_end):
        if page_idx == 0:
            url = raw_url + '?sh=8c6357fe75677b0de345ac6b12f734cfa3a8c895'
        else:
            url = raw_url + ('?offset=%d' % (page_idx * 100)) + '&sh=8c6357fe75677b0de345ac6b12f734cfa3a8c895'

        flag, img_urls = collect_image_url(url)
        if not flag:
            print('invalid url %s' % url)
            continue
        else:
            image_urls += img_urls
    print(f'page index from {page_start} to {page_end - 1} have {len(image_urls)} image urls.')
    all_image_urls += image_urls


class spiderThread(threading.Thread):
    def __init__(self, name, raw_url, idx_start, idx_end):
        threading.Thread.__init__(self);
        self.thread_name = name;
        self.raw_url = raw_url
        self.idx_start = idx_start
        self.idx_end = idx_end

    def run(self):
        spider_images(self.raw_url, self.idx_start, self.idx_end)


class downloadThread(threading.Thread):
    def __init__(self, name, img_save_path, image_urls, idx_start, idx_end):
        threading.Thread.__init__(self);
        self.thread_name = name;
        self.img_save_path = img_save_path
        self.image_urls = image_urls
        self.idx_start = idx_start
        self.idx_end = idx_end

    def run(self):
        download(self.img_save_path, self.image_urls[self.idx_start:self.idx_end], self.thread_name)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-num_thread', '--num_thread', default=50, type=int)
    parser.add_argument('-each_task', '--each_task', default=400, type=int)
    parser.add_argument('-url', '--url', default='https://cn.depositphotos.com/stock-photos/portrait.html', type=str)
    parser.add_argument('-spider_image', '--spider_image', default=False, action='store_true')
    parser.add_argument('-url_save_path', '--url_save_path', default='url_images.json', type=str)
    parser.add_argument('-download_image', '--download_image', default=False, action='store_true')
    parser.add_argument('-img_save_path', '--img_save_path', default='append_images', type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()

    raw_url = args.url

    if args.spider_image:
        start = time.time()

        threads = []
        page_start, page_end = 0, 0
        for i in range(args.num_thread):
            page_start = page_end
            page_end = page_start + args.each_task
            thread = spiderThread(i, raw_url, page_start, page_end)
            threads.append(thread)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        image_urls = remove_repeated_url()
        with open(args.url_save_path, 'w') as file:
            json.dump(image_urls, file)

        end = time.time()
        print('total cost time for spiding images: ', end - start)

    elif args.download_image:
        start = time.time()
        os.makedirs(args.img_save_path, exist_ok=False)
        with open(args.url_save_path, 'r') as file:
            image_urls = json.load(file)
        num_total = len(image_urls)
        each_task = num_total // args.num_thread

        threads = []
        idx_start, idx_end = 0, 0
        for i in range(args.num_thread):
            idx_start = idx_end
            idx_end = idx_start + each_task
            if i == args.num_thread - 1:
                idx_end = num_total
            thread = downloadThread(i, args.img_save_path, image_urls, idx_start, idx_end)
            threads.append(thread)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        end = time.time()
        print('total cost time for downloading %d images: ' % num_images, end - start)