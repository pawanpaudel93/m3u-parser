#!/usr/bin/env python3

import asyncio
import json
import logging
import random
import re
import sys
import aiohttp
import pycountry
import requests
import time
import ssl
from urllib.parse import urlparse, unquote

try:
    from helper import is_present, ndict_to_csv, run_until_completed
except ModuleNotFoundError:
    from .helper import is_present, ndict_to_csv, run_until_completed

ssl.match_hostname = lambda cert, hostname: hostname == cert['subjectAltName'][0][1]
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)


class M3uParser:
    """A parser for m3u files.

    It parses the contents of m3u file to a list of streams information which can be saved as a JSON/CSV file.

    :Example

    >>> url = "/home/pawan/Downloads/ru.m3u"
    >>> useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
    >>> m3u_playlist = M3uParser(timeout=5, useragent=useragent)
    >>> m3u_playlist.parse_m3u(url)
    INFO: Started parsing m3u file...
    >>> m3u_playlist.remove_by_extension('mp4')
    >>> m3u_playlist.filter_by('status', 'GOOD')
    >>> print(len(m3u_playlist.get_list()))
    4
    >> m3u_playlist.to_file('pawan.json')
    INFO: Saving to file...
    """

    def __init__(self, useragent=None, timeout=5):
        self.__streams_info = []
        self.__streams_info_backup = []
        self.__lines = []
        self.__timeout = timeout
        self.__loop = None
        self.__headers = {
            "User-Agent": useragent
            if useragent
            else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        self.__check_live = False
        self.__content = ""
        self.__url_regex = re.compile(
            r"^(?:(?:https?|ftp)://)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!("
            r"?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,"
            r"3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){"
            r"2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*["
            r"a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*["
            r"a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?$"
        )
        self.__file_regex = re.compile(r"^[a-zA-Z]:\\((?:.*?\\)*).*\.[\d\w]{3,5}$|^(/[^/]*)+/?.[\d\w]{3,5}$")

    def parse_m3u(self, path, check_live=True):
        """Parses the content of local file/URL.

        It downloads the file from the given url or use the local file path to get the content and parses line by line
        to a structured format of streams information.

        :param path: Path can be a url or local filepath
        :type path: str
        :param check_live: To check if the stream links are working or not
        :type check_live: bool
        :rtype: None

        """
        self.__check_live = check_live
        if urlparse(path).scheme != "" or re.search(self.__url_regex, path):
            logging.info("Started parsing m3u link...")
            try:
                self.__content = requests.get(path).text
            except:
                logging.info("Cannot read anything from the url!!!")
                return
        else:
            logging.info("Started parsing m3u file...")
            try:
                with open(unquote(path), errors="ignore") as fp:
                    self.__content = fp.read()
            except FileNotFoundError:
                logging.info("File doesn't exist!!!")
                return

        # splitting contents into lines to parse them
        self.__lines = [
            line.strip("\n\r")
            for line in self.__content.split("\n")
            if line.strip("\n\r") != ""
        ]
        if len(self.__lines) > 0:
            self.__parse_lines()
        else:
            logging.info("No content to parse!!!")

    @staticmethod
    async def __run_until_completed(tasks):
        for res in run_until_completed(tasks):
            _ = await res

    def __parse_lines(self):
        num_lines = len(self.__lines)
        self.__streams_info.clear()
        try:
            self.__loop = asyncio.get_event_loop()
        except RuntimeError:
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)
        try:
            coros = (
                self.__parse_line(line_num)
                for line_num in range(num_lines)
                if "#EXTINF" in self.__lines[line_num]
            )
            self.__loop.run_until_complete(self.__run_until_completed(coros))
        except BaseException:
            pass
        else:
            self.__streams_info_backup = self.__streams_info.copy()
            self.__loop.run_until_complete(asyncio.sleep(0))
            while self.__loop.is_running():
                time.sleep(0.3)
                if not self.__loop.is_running():
                    self.__loop.close()
                    break
        logging.info("Parsing completed !!!")

    async def __parse_line(self, line_num):
        line_info = self.__lines[line_num]
        stream_link = ""
        streams_link = []
        status = "BAD"
        try:
            for i in [1, 2]:
                if self.__lines[line_num + i] and re.search(
                    self.__url_regex, self.__lines[line_num + i]
                ):
                    streams_link.append(self.__lines[line_num + i])
                    break
                elif self.__lines[line_num + i] and re.search(
                    self.__file_regex, self.__lines[line_num + i]
                ):
                    status = "GOOD"
                    streams_link.append(self.__lines[line_num +i])
                    break
            stream_link = streams_link[0]
        except IndexError:
            pass
        if line_info and stream_link:
            try:
                tvg_name = is_present(r"tvg-name=\"(.*?)\"", line_info)
                tvg_id = is_present(r"tvg-id=\"(.*?)\"", line_info)
                logo = is_present(r"tvg-logo=\"(.*?)\"", line_info)
                category = is_present(r"group-title=\"(.*?)\"", line_info)
                title = is_present("[,](?!.*[,])(.*?)$", line_info)
                country = is_present(r"tvg-country=\"(.*?)\"", line_info)
                language = is_present(r"tvg-language=\"(.*?)\"", line_info)
                tvg_url = is_present(r"tvg-url=\"(.*?)\"", line_info)
                country_obj = pycountry.countries.get(alpha_2=country.upper())
                language_obj = pycountry.languages.get(name=country.capitalize())
                country_name = country_obj.name if country_obj else ""
                language_code = language_obj.alpha_3 if language_obj else ""

                timeout = aiohttp.ClientTimeout(total=self.__timeout)
                if self.__check_live and status == "BAD":
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.request(
                                "get",
                                stream_link,
                                headers=self.__headers,
                                timeout=timeout,
                            ) as response:
                                if response.status == 200:
                                    status = "GOOD"
                    except:
                        pass
                temp = {
                    "name": title,
                    "logo": logo,
                    "url": stream_link,
                    "category": category,
                    "language": {
                        "code": language_code,
                        "name": language,
                    },
                    "country": {"code": country, "name": country_name},
                    "tvg": {
                        "id": tvg_id,
                        "name": tvg_name,
                        "url": tvg_url,
                    },
                }
                if self.__check_live:
                    temp["status"] = status
                self.__streams_info.append(temp)
            except AttributeError:
                pass

    def filter_by(self, key, filters, retrieve=True, nested_key=False):
        """Filter streams infomation.

        It retrieves/removes stream information from streams information list using filter/s on key.

        :param key: Key can be single or nested. eg. key='name', key='language-name'
        :type key: str
        :param filters: List of filter/s to perform the retrieve or remove operation.
        :type filters: str or list
        :param retrieve: True to retrieve and False for removing based on key.
        :type retrieve: bool
        :param nested_key: True/False for if the key is nested or not.
        :type nested_key: bool
        :rtype: None
        """
        key_0, key_1 = [""] * 2
        if nested_key:
            key_0, key_1 = key.split("-")
        if not filters:
            logging.info("Filter word/s missing!!!")
            return []
        if not isinstance(filters, list):
            filters = [filters]
        if retrieve:
            try:
                self.__streams_info = list(
                    filter(
                        lambda stream_info: any(
                            [
                                re.search(
                                    re.compile(fltr, flags=re.IGNORECASE),
                                    stream_info[key_0][key_1]
                                    if nested_key
                                    else stream_info[key],
                                )
                                for fltr in filters
                            ]
                        ),
                        self.__streams_info,
                    )
                )
            except KeyError:
                print(f"{key} is missing in stream info")
        else:
            try:
                self.__streams_info = list(
                    filter(
                        lambda stream_info: any(
                            [
                                not re.search(
                                    re.compile(fltr, flags=re.IGNORECASE),
                                    stream_info[key_0][key_1]
                                    if nested_key
                                    else stream_info[key],
                                )
                                for fltr in filters
                            ]
                        ),
                        self.__streams_info,
                    )
                )
            except KeyError:
                print(f"{key} is missing in stream info")

    def reset_operations(self):
        """Reset the stream information list to initial state before various operations.

        :rtype: None
        """
        self.__streams_info = self.__streams_info_backup.copy()

    def remove_by_extension(self, extension):
        """Remove stream information with certain extension/s.

        It removes stream information from streams information list based on extension/s provided.

        :param extension: Name of the extension like mp4, m3u8 etc. It can be a string or list of extension/s.
        :type extension: str or list
        :rtype: None
        """
        self.filter_by("url", extension, retrieve=False, nested_key=False)

    def retrieve_by_extension(self, extension):
        """Select only streams information with a certain extension/s.

        It retrieves the stream information based on extension/s provided.

        :param extension: Name of the extension like mp4, m3u8 etc. It can be a string or list of extension/s.
        :type extension: str or list
        :rtype: None
        """
        self.filter_by("url", extension, retrieve=True, nested_key=False)

    def remove_by_category(self, filter_word):
        """Removes streams information with category containing a certain filter word/s.

        It removes stream information based on category using filter word/s.

        :param filter_word: It can be a string or list of filter word/s.
        :type filter_word: str or list
        :rtype: None
        """
        self.filter_by("category", filter_word, retrieve=False)

    def retrieve_by_category(self, filter_word):
        """Retrieve only streams information that contains a certain filter word/s.

        It retrieves stream information based on category/categories.

        :param filter_word: It can be a string or list of filter word/s.
        :type filter_word: str or list
        :rtype: None
        """
        self.filter_by("category", filter_word, retrieve=True)

    def sort_by(self, key, asc=True, nested_key=False):
        """Sort streams information.

        It sorts streams information list sorting by key in asc/desc order.

        :param key: It can be single or nested key.
        :type key: str
        :param asc: Sort by asc or desc order
        :type asc: bool
        :param nested_key: True/False for if the key is nested or not.
        :type nested_key: bool
        :rtype: None
        """
        key_0, key_1 = [""] * 2
        if nested_key:
            key_0, key_1 = key.split("-")
        self.__streams_info = sorted(
            self.__streams_info,
            key=lambda stream_info: stream_info[key_0][key_1]
            if nested_key
            else stream_info[key],
            reverse=not asc,
        )

    def get_json(self, indent=4):
        """Get the streams information as json.

        :param indent: Int value for indentation.
        :type indent: int
        :return: json of the streams_info list
        :rtype: json
        """
        return json.dumps(self.__streams_info, indent=indent)

    def get_list(self):
        """Get the parsed streams information list.

        It returns the streams information list.

        :return: Streams information list
        :rtype: list
        """
        return self.__streams_info

    def get_random_stream(self, random_shuffle=True):
        """Return a random stream information

        It returns a random stream information with shuffle if required.

        :param random_shuffle: To shuffle the streams information list before returning the random stream information.
        :type random_shuffle: bool
        :return: A random stream info
        :rtype: dict
        """
        if not len(self.__streams_info):
            logging.info("No streams information so could not get any random stream.")
            return None
        if random_shuffle:
            random.shuffle(self.__streams_info)
        return random.choice(self.__streams_info)

    def to_file(self, filename, format="json"):
        """Save to file (CSV or JSON)

        It saves streams information as a CSV or JSON file with a given filename and format parameters.

        :param filename: Name of the file to save streams_info as.
        :type filename: str
        :param format: csv/json to save the streams_info.
        :type format: str
        :rtype: None
        """
        format = filename.split(".")[-1] if len(filename.split(".")) > 1 else format

        def with_extension(name, ext):
            name, ext = name.lower(), ext.lower()
            if ext in name:
                return name
            else:
                return name + f".{ext}"
        
        filename = with_extension(filename, format)
        logging.info("Saving to file: %s"%filename)
        try:
            if format == "json":
                data = json.dumps(self.__streams_info, indent=4)
                with open(filename, "w") as fp:
                    fp.write(data)
                logging.info("Saved to file: %s"%filename)

            elif format == "csv":
                ndict_to_csv(self.__streams_info, filename)
                logging.info("Saved to file: %s"%filename)
            else:
                logging.info("Unrecognised format!!!")
        except Exception as error:
            logging.warning(str(error))


if __name__ == "__main__":
    url = "/home/pawan/Downloads/ru.m3u"
    useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
    m3u_playlist = M3uParser(timeout=5, useragent=useragent)
    m3u_playlist.parse_m3u(url)
    m3u_playlist.remove_by_extension("mp4")
    m3u_playlist.filter_by("status", "GOOD")
    print(len(m3u_playlist.get_list()))
    m3u_playlist.to_file("pawan.json")
