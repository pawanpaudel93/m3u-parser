#!/usr/bin/env python3

import asyncio
import csv
import json
import logging
import random
import re
import sys
import aiohttp
import pycountry
import requests
from urllib.parse import urlparse

from helper import is_present, ndict_to_csv

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s")


class M3uParser:
    def __init__(self, useragent, timeout=5):
        self.streams_info = []
        self.lines = []
        self.timeout = timeout
        self.headers = {
            'User-Agent': useragent
        }
        self.check_live = False
        self.content = ""
        self.url_regex = re.compile(r"^(?:(?:https?|ftp)://)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!("
                                    r"?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,"
                                    r"3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){"
                                    r"2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*["
                                    r"a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*["
                                    r"a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?$")

    # Download the file from the given url or use the local file path to get the content
    def parse_m3u(self, url, check_live=False):
        self.check_live = check_live
        if urlparse(url).scheme != '' or re.search(self.url_regex, url):
            try:
                self.content = requests.get(url).text
            except:
                logging.info("Cannot read anything from the url!!!")
                exit()
        else:
            try:
                with open(url, errors='ignore') as fp:
                    self.content = fp.read()
            except FileNotFoundError:
                logging.info("File doesn't exist!!!")
                exit()
        # splitting contents into lines to parse them
        self.lines = [line.strip('\n\r') for line in self.content.split("\n") if line.strip('\n\r') != '']
        if len(self.lines) > 0:
            self.__parse_lines()
        else:
            logging.info("No content to parse!!!")

    # parse each lines and extract the streams information
    def __parse_lines(self):
        num_lines = len(self.lines)
        try:
            loop = asyncio.get_event_loop()
            f = asyncio.wait(
                [self.__parse_line(line_num) for line_num in range(num_lines) if "#EXTINF" in self.lines[line_num]], return_when=asyncio.ALL_COMPLETED)
            loop.run_until_complete(f)
        except:
            pass
        finally:
            loop.close()

    async def __parse_line(self, line_num):
        line_info = self.lines[line_num]
        stream_link = ''
        streams_link = []
        try:
            for i in [1, 2]:
                if self.lines[line_num + i] and re.search(self.url_regex, self.lines[line_num + i]):
                    streams_link.append(self.lines[line_num + i])
                    break
            stream_link = streams_link[0]
        except IndexError:
            pass
        if line_info and stream_link:
            try:
                tvg_name = is_present(r"tvg-name=\"(.*?)\"", line_info)
                tvg_id = is_present(r"tvg-id=\"(.*?)\"", line_info)
                logo = is_present(r"tvg-logo=\"(.*?)\"", line_info)
                group = is_present(r"group-title=\"(.*?)\"", line_info)
                title = is_present("[,](?!.*[,])(.*?)$", line_info)
                country = is_present(r"tvg-country=\"(.*?)\"", line_info)
                language = is_present(r"tvg-language=\"(.*?)\"", line_info)
                tvg_url = is_present(r"tvg-url=\"(.*?)\"", line_info)
                country_obj = pycountry.countries.get(alpha_2=country.upper())
                language_obj = pycountry.languages.get(name=country.capitalize())
                country_name = country_obj.name if country_obj else ''
                language_code = language_obj.alpha_3 if language_obj else ''

                timeout = aiohttp.ClientTimeout(total=self.timeout)
                status = 'BAD'
                if self.check_live:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.request('get', stream_link, headers=self.headers,
                                                       timeout=timeout) as response:
                                if response.status == 200:
                                    status = 'GOOD'
                    except:
                        pass
                temp = {
                    "name": title,
                    "logo": logo,
                    "url": stream_link,
                    "category": group,
                    "language": {
                        "code": language_code,
                        "name": language,
                    },
                    "country": {
                        "code": country,
                        "name": country_name
                    },
                    "tvg": {
                        "id": tvg_id,
                        "name": tvg_name,
                        "url": tvg_url,
                    }
                }
                if self.check_live:
                    temp['status'] = status
                self.streams_info.append(temp)
            except AttributeError:
                pass

    def filter_by(self, key, filters, retrieve=True, nested_key=False):
        key_0, key_1 = ['']*2
        if nested_key:
            key_0, key_1 = key.split('-')
        if not filters:
            logging.info("Filter word/s missing!!!")
            return []
        if not isinstance(filters, list):
            filters = [filters]
        if retrieve:
            self.streams_info = list(filter(
                lambda file: any(
                    [re.search(re.compile(fltr, flags=re.IGNORECASE), file[key_0][key_1] if nested_key else file[key])
                     for fltr in filters]),
                self.streams_info))
        else:
            self.streams_info = list(filter(
                lambda file: any([not re.search(re.compile(fltr, flags=re.IGNORECASE),
                                                file[key_0][key_1] if nested_key else file[key]) for fltr in filters]),
                self.streams_info))

    # Remove streams_info with a certain file extension
    def remove_by_extension(self, extension):
        self.filter_by('tvg-url', extension, retrieve=False, nested_key=True)

    # Select only streams_info with a certain file extension
    def retrieve_by_extension(self, extension):
        self.filter_by('tvg-url', extension, retrieve=True, nested_key=True)

    # Remove streams_info that contains a certain filter word
    def remove_by_grpname(self, filter_word):
        self.filter_by('category', filter_word, retrieve=False)

    # Retrieve only streams_info that contains a certain filter word
    def retrieve_by_grpname(self, filter_word):
        self.filter_by('category', filter_word, retrieve=True)

    # sort the streams_info
    def sort_by(self, key, asc=True, nested_key=False):
        key_0, key_1 = ['']*2
        if nested_key:
            key_0, key_1 = key.split('-')
        self.streams_info = sorted(self.streams_info, key=lambda file: file[key_0][key_1] if nested_key else file[key],
                                   reverse=not asc)

    # Get the streams info as json
    def get_json(self):
        return json.dumps(self.streams_info, indent=4)

    # Get the streams info as dict
    def get_dict(self):
        return self.streams_info

    # Return a random stream information
    def get_random_stream(self, random_shuffle=True):
        if not len(self.streams_info):
            logging.info("No streams information so could not get any random stream.")
            return None
        if random_shuffle: random.shuffle(self.streams_info)
        return random.choice(self.streams_info)

    # save to file (CSV or JSON)
    def to_file(self, filename, format='json'):
        format = filename.split('.')[-1] if len(filename.split('.')) > 1 else format

        def with_extension(name, ext):
            name, ext = name.lower(), ext.lower()
            if ext in name:
                return name
            else:
                return name + f".{ext}"

        if format == 'json':
            data = json.dumps(self.streams_info, indent=4)
            with open(with_extension(filename, format), 'w') as fp:
                fp.write(data)

        elif format == 'csv':
            ndict_to_csv(self.streams_info, with_extension(filename, format))
        else:
            logging.info("Unrecognised format!!!")


if __name__ == "__main__":
    url = "https://iptv-org.github.io/iptv/categories/music.m3u"
    timeout = 5
    useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    m3u_playlist = M3uParser(timeout=timeout, useragent=useragent)
    m3u_playlist.parse_m3u(url, check_live=True)
    m3u_playlist.remove_by_extension('m3u8')
    m3u_playlist.remove_by_grpname('Zimbabwe')
    m3u_playlist.filter_by('language-name', 'Hungarian', retrieve=False, nested_key=True)
    m3u_playlist.filter_by('status', 'GOOD')
    print(len(m3u_playlist.get_dict()))
    m3u_playlist.to_file('pawan.json')
