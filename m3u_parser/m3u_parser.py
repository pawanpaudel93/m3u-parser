#!/usr/bin/env python3

import asyncio
import csv
import json
import random
import re
import ssl
import time
import string
from typing import Union

import aiohttp
import pycountry
import urllib.request

from .exceptions import (
    KeyNotFoundException,
    NestedKeyException,
    NoContentToParseException,
    NoStreamsException,
    SavingNotSupportedException,
    UnrecognizedFormatException,
    UrlReadException,
    ParamNotPassedException,
)
from .helper import (
    default_useragent,
    get_by_regex,
    is_valid_url,
    ndict_to_csv,
    run_until_completed,
    setup_logger,
)

ssl.match_hostname = lambda cert, hostname: hostname == cert["subjectAltName"][0][1]

logger = setup_logger()


class M3uParser:
    """A parser for m3u files.

    This class parses the contents of M3U files into a list of stream information, which can be saved as a JSON, CSV, or M3U file.

    Args:
        - `useragent` (str, optional): User agent string for HTTP requests. Defaults to default_useragent.
        - `timeout` (int, optional): Timeout duration for HTTP requests in seconds. Defaults to 5.


    Example::

        url = "/home/pawan/Downloads/ru.m3u"
        useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        parser = M3uParser(timeout=5, useragent=useragent)
        parser.parse_m3u(url)
        # INFO: Started parsing m3u file...
        parser.remove_by_extension('mp4')
        parser.filter_by('status', 'GOOD')
        print(len(parser.get_list()))
        # 4
        parser.to_file('pawan.json')
        # INFO: Saving to file...
    """

    def __init__(self, useragent: str = default_useragent, timeout: int = 5):
        self._streams_info = []
        self._streams_info_backup = []
        self._lines = []
        self._status_checker = {}
        self._schemes = set()
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._loop = None
        self._enforce_schema = True
        self._headers = {"User-Agent": useragent if useragent else default_useragent}
        self._check_live = False
        self._file_regex = re.compile(r"^[a-zA-Z]:\\((?:.*?\\)*).*\.[\d\w]{3,5}$|^(/[^/]*)+/?.[\d\w]{3,5}$")
        self._tvg_name_regex = re.compile(r"tvg-name=\"(.*?)\"", flags=re.IGNORECASE)
        self._tvg_id_regex = re.compile(r"tvg-id=\"(.*?)\"", flags=re.IGNORECASE)
        self._logo_regex = re.compile(r"tvg-logo=\"(.*?)\"", flags=re.IGNORECASE)
        self._category_regex = re.compile(r"group-title=\"(.*?)\"", flags=re.IGNORECASE)
        self._title_regex = re.compile(r"(?!.*=\",?.*\")[,](.*?)$", flags=re.IGNORECASE)
        self._country_regex = re.compile(r"tvg-country=\"(.*?)\"", flags=re.IGNORECASE)
        self._language_regex = re.compile(r"tvg-language=\"(.*?)\"", flags=re.IGNORECASE)
        self._tvg_url_regex = re.compile(r"tvg-url=\"(.*?)\"", flags=re.IGNORECASE)

    def _read_content(self, path: str, type="m3u"):
        content = ""
        if is_valid_url(path):
            logger.info(f"Started parsing {type} link...")
            try:
                with urllib.request.urlopen(path) as response:
                    content_type = response.getheader('Content-Type')
                    content = response.read()
                    try:
                        encoding = (
                            content_type.split('charset=')[-1].split(";")[0].strip(string.whitespace + "'\" ")
                            if (content_type and 'charset=' in content_type)
                            else "utf-8"
                        )
                        content = content.decode(encoding)
                    except:
                        content = content.decode("utf-8")
            except:
                raise UrlReadException("Cannot read anything from the url.")
        else:
            logger.info(f"Started parsing {type} file...")
            try:
                with open(path, encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
            except FileNotFoundError:
                raise FileNotFoundError("File doesn't exist.")
        return content

    @staticmethod
    async def _run_until_completed(tasks):
        for res in run_until_completed(tasks):
            _ = await res

    def _set_event_loop(self):
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    def _close_loop(self):
        while self._loop.is_running():
            time.sleep(0.3)
            if not self._loop.is_running():
                self._loop.close()
                break

    def _parse_lines(self):
        num_lines = len(self._lines)
        self._streams_info.clear()
        self._set_event_loop()
        coros = (self._parse_line(line_num) for line_num in range(num_lines) if "#EXTINF" in self._lines[line_num])
        self._loop.run_until_complete(self._run_until_completed(coros))
        self._loop.run_until_complete(asyncio.sleep(0))
        self._streams_info_backup = self._streams_info.copy()
        self._close_loop()
        logger.info("Parsing completed.")

    async def _get_status(self, stream_link):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    "get",
                    stream_link,
                    headers=self._headers,
                    timeout=self._timeout,
                ) as response:
                    if response.status == 200:
                        return True
        except:
            pass
        return False

    async def _check_status(self, index):
        stream_info = self._streams_info[index]
        stream_url = stream_info.get("url")
        scheme = stream_url.split('://')[0].lower()
        status_fn = self._status_checker.get(scheme)
        if status_fn is None or not callable(status_fn):
            status_fn = self._get_status
        stream_info["status"] = "GOOD" if await status_fn(stream_url) == True else "BAD"
        stream_info["live"] = stream_info["status"] == "GOOD"
        self._streams_info[index] = stream_info

    def _check_streams_status(self):
        if self._check_live and len(self._streams_info) > 0:
            self._set_event_loop()
            coros = (self._check_status(index) for index in range(len(self._streams_info)))
            self._loop.run_until_complete(self._run_until_completed(coros))
            self._loop.run_until_complete(asyncio.sleep(0))
            self._streams_info_backup = self._streams_info.copy()
            self._close_loop()
        logger.info("Parsing completed.")

    async def _parse_line(self, line_num: int):
        line_info = self._lines[line_num]
        stream_link = ""
        streams_link = []
        status = "BAD"
        try:
            for i in [1, 2]:
                if self._lines[line_num + i] and (is_valid_url(self._lines[line_num + i], self._schemes)):
                    streams_link.append(self._lines[line_num + i])
                    break
                elif self._lines[line_num + i] and re.search(self._file_regex, self._lines[line_num + i]):
                    status = "GOOD"
                    streams_link.append(self._lines[line_num + i])
                    break
            stream_link = streams_link[0]
        except IndexError:
            pass
        if line_info and stream_link:
            info = {}
            # Title
            title = get_by_regex(self._title_regex, line_info)
            if title != None or self._enforce_schema:
                info["name"] = title
            # Logo
            logo = get_by_regex(self._logo_regex, line_info)
            if logo != None or self._enforce_schema:
                info["logo"] = logo
            info["url"] = stream_link
            # Category
            category = get_by_regex(self._category_regex, line_info)
            if category != None or self._enforce_schema:
                info["category"] = category
            # TVG information
            tvg_id = get_by_regex(self._tvg_id_regex, line_info)
            tvg_name = get_by_regex(self._tvg_name_regex, line_info)
            tvg_url = get_by_regex(self._tvg_url_regex, line_info)
            if tvg_id != None or tvg_name != None or tvg_url != None or self._enforce_schema:
                info["tvg"] = {}
                for key, val in zip(["id", "name", "url"], [tvg_id, tvg_name, tvg_url]):
                    if val != None or self._enforce_schema:
                        info["tvg"][key] = val
            # Country
            country = get_by_regex(self._country_regex, line_info)
            if country != None or self._enforce_schema:
                country_obj = pycountry.countries.get(alpha_2=country if country else "")
                info["country"] = {
                    "code": country,
                    "name": country_obj.name if country_obj else None,
                }
            # Language
            language = get_by_regex(self._language_regex, line_info)
            if language != None or self._enforce_schema:
                language_obj = pycountry.languages.get(name=language if language else "")
                info["language"] = {
                    "code": language_obj.alpha_3 if language_obj else None,
                    "name": language,
                }

            if self._check_live and status == "BAD":
                scheme = stream_link.split('://')[0].lower()
                status_fn = self._status_checker.get(scheme)
                if status_fn is None or not callable(status_fn):
                    status_fn = self._get_status
                status = "GOOD" if await status_fn(stream_link) == True else "BAD"
            if self._check_live:
                info["status"] = status
                info["live"] = status == "GOOD"
            self._streams_info.append(info)

    @staticmethod
    def _get_m3u_content(streams_info: list) -> str:
        """Save the streams information list to m3u file.

        It saves the streams information list to m3u file.

        :rtype: None
        """
        if len(streams_info) == 0:
            return ""
        content = ["#EXTM3U"]
        for stream_info in streams_info:
            line = "#EXTINF:-1"
            if stream_info.get("tvg") != None:
                for key, value in stream_info["tvg"].items():
                    if value != None:
                        line += ' tvg-{}="{}"'.format(key, value)
            if stream_info.get("logo") != None:
                line += ' tvg-logo="{}"'.format(stream_info["logo"])
            if stream_info.get("country") != None and stream_info["country"].get("code") != None:
                line += ' tvg-country="{}"'.format(stream_info["country"]["code"])
            if stream_info.get("language") != None and stream_info["language"].get("name") != None:
                line += ' tvg-language="{}"'.format(stream_info["language"]["name"])
            if stream_info.get("category") != None:
                line += ' group-title="{}"'.format(stream_info["category"])
            if stream_info.get("name") != None:
                line += ',' + stream_info['name']
            content.append(line)
            content.append(stream_info["url"])
        return "\n".join(content)

    def parse_m3u(
        self,
        data_source: str,
        schemes=['http', 'https', 'ftp', 'ftps'],
        status_checker=dict(),
        check_live=True,
        enforce_schema=True,
    ):
        """
        Parses the content of a local M3U file or URL.

        Downloads the file from the given URL or uses the local file path to parse its content.
        It then processes the M3U file line by line, converting it into a structured format of streams information.

        Args:
            - `data_source` (str): The file path or URL of the M3U file to be parsed.
            - `schemes` (list): A list of allowed URL schemes. Default is ["http", "https", "ftp", "ftps"].
            - `status_checker` (dict): A dictionary mapping URL schemes to custom status checker functions.
            - `check_live` (bool): Indicates whether to check the status of live streams (default is True).
            - `enforce_schema` (bool): Indicates whether to enforce a specific schema for parsed data.
                If enforced, non-existing fields in a stream are filled with None/null.
                If not enforced, non-existing fields are ignored.

        Raises:
            - `NoContentToParseException`: Raised if there is no content to parse in the M3U file.
            - `UrlReadException`: Raised when there is an issue reading content from a URL.
            - `FileNotFoundError`: Raised if the file does not exist or is not accessible.

        Returns:
            None: The parsed streams information is stored internally and can be accessed using other methods.

        Example::

            async def ftp_checker(url: str) -> bool:
                # Checker implementation
                # Return either True for good status or False for bad status
                return True

            parse_m3u("https://example.com/np.m3u", schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)
        """
        content = ""
        self._check_live = check_live
        self._enforce_schema = enforce_schema
        self._status_checker = status_checker
        self._schemes = set(schemes)

        content = self._read_content(data_source, "m3u")

        # splitting contents into lines to parse them
        self._lines = [line.strip("\n\r") for line in content.split("\n") if line.strip("\n\r") != ""]
        if len(self._lines) > 0:
            self._parse_lines()
        else:
            raise NoContentToParseException("No content to parse.")

    def parse_json(
        self,
        data_source: str,
        schemes=['http', 'https', 'ftp', 'ftps'],
        status_checker=dict(),
        check_live=True,
        enforce_schema=True,
    ):
        """
        Parses the content of a local JSON file or JSON URL.

        Downloads the JSON data from the given URL or uses the local file path to parse its content.
        It expects the JSON data to be in a specific structure representing streams information.
        The parsed information is processed and stored internally for further operations.

        Args:
            - `data_source` (str): The file path or URL of the JSON file containing streams information.
            - `schemes` (list): A list of allowed URL schemes. Default is ["http", "https", "ftp", "ftps"].
            - `status_checker` (dict): A dictionary mapping URL schemes to custom status checker functions.
            - `check_live` (bool): Indicates whether to check the status of live streams (default is True).
            - `enforce_schema` (bool): Indicates whether to enforce a specific schema for parsed data.
                If enforced, non-existing fields in a stream are filled with None/null.
                If not enforced, non-existing fields are ignored.

        Raises:
            - `UrlReadException`: Raised when there is an issue reading content from a URL.
            - `FileNotFoundError`: Raised if the file does not exist or is not accessible.

        Returns:
            None: The parsed streams information is stored internally and can be accessed using other methods.

        Example::

            async def ftp_checker(url: str) -> bool:
                # Checker implementation
                # Return either True for good status or False for bad status
                return True

            parse_json("https://example.com/np.json", schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)

        """
        content = ""
        self._check_live = check_live
        self._enforce_schema = enforce_schema
        self._status_checker = status_checker
        self._schemes = set(schemes)

        content = self._read_content(data_source, "json")

        streams_info = json.loads(content)
        if streams_info and type(streams_info) == list and len(streams_info) > 0:
            self._streams_info = [
                {
                    "name": stream_info.get("name"),
                    "logo": stream_info.get("logo"),
                    "url": stream_info.get("url"),
                    "category": stream_info.get("category"),
                    "tvg": {
                        "id": stream_info.get("tvg_id"),
                        "name": stream_info.get("tvg_name"),
                        "url": stream_info.get("tvg_url"),
                    },
                    "country": {"code": stream_info.get("country_code"), "name": stream_info.get("country_name")},
                    "language": {"code": stream_info.get("language_code"), "name": stream_info.get("language_name")},
                    "status": stream_info.get("status") or "BAD",
                    "live": stream_info.get("status") == "GOOD",
                }
                for stream_info in streams_info
                if type(stream_info) == dict and stream_info.get("url")
            ]
        self._check_streams_status()

    def parse_csv(
        self,
        data_source: str,
        schemes=['http', 'https', 'ftp', 'ftps'],
        status_checker=dict(),
        check_live=True,
        enforce_schema=True,
    ):
        """
        Parses the content of a local CSV file or CSV URL.

        Downloads the CSV data from the given URL or uses the local file path to parse its content.
        It expects the CSV data to be in a specific structure representing streams information.
        The parsed information is processed and stored internally for further operations.

        Args:
            - `data_source` (str): The file path or URL of the CSV file containing streams information.
            - `schemes` (list): A list of allowed URL schemes. Default is ["http", "https", "ftp", "ftps"].
            - `status_checker` (dict): A dictionary mapping URL schemes to custom status checker functions.
            - `check_live` (bool): Indicates whether to check the status of live streams (default is True).
            - `enforce_schema` (bool): Indicates whether to enforce a specific schema for parsed data.
                If enforced, non-existing fields in a stream are filled with None/null.
                If not enforced, non-existing fields are ignored.

        Raises:
            - `UrlReadException`: Raised when there is an issue reading content from a URL.
            - `FileNotFoundError`: Raised if the file does not exist or is not accessible.

        Returns:
            None: The parsed streams information is stored internally and can be accessed using other methods.

        Example::

            async def ftp_checker(url: str) -> bool:
                # Checker implementation
                # Return either True for good status or False for bad status
                return True

            parse_csv("https://example.com/np.csv", schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)
        """
        content = ""
        self._check_live = check_live
        self._enforce_schema = enforce_schema
        self._status_checker = status_checker
        self._schemes = set(schemes)

        content = self._read_content(data_source, "csv")

        reader = csv.DictReader(content.splitlines(), delimiter=",")
        get_value = lambda row, key: row.get(key) or None
        self._streams_info = [
            {
                "name": get_value(row, "name"),
                "logo": get_value(row, "logo"),
                "url": get_value(row, "url"),
                "category": get_value(row, "category"),
                "tvg": {
                    "id": get_value(row, "tvg_id"),
                    "name": get_value(row, "tvg_name"),
                    "url": get_value(row, "tvg_url"),
                },
                "country": {"code": get_value(row, "country_code"), "name": get_value(row, "country_name")},
                "language": {"code": get_value(row, "language_code"), "name": get_value(row, "language_name")},
                "status": get_value(row, "status") or "BAD",
                "live": get_value(row, "status") == "GOOD",
            }
            for row in reader
            if get_value(row, "url")
        ]
        self._check_streams_status()

    def filter_by(
        self,
        key: str,
        filters: Union[str, list[Union[str, None, bool]], None, bool],
        key_splitter: str = "-",
        retrieve: bool = True,
        nested_key: bool = False,
    ):
        """
        Filter streams information based on a specific key and filter criteria.

        Filters the internal streams information list based on the provided key and filter words.
        If the key is not found or if the filter words do not match any stream information, the filtering is done silently.

        Args:
            - `key` (str): The key to filter by. It can be a nested key separated by a splitter if 'nested_key' is True in config.
            - `filters` (Union[str, list[Union[str, None, bool]], None, bool]): Filter word or list of filter words to perform the filtering operation.
            - `key_splitter` (str): A string used to split nested keys (default is "-").
            - `retrieve` (bool): Indicates whether to retrieve or remove based on the filter key (default is True).
            - `nested_key` (bool): Indicates whether the filter key is nested or not (default is False).

        Raises:
            - `NestedKeyException`: Raised if 'nested_key' is True but the key is not in the correct format.
            - `KeyNotFoundException`: Raised if key is missing in the streams.

        Returns:
            None: The internal streams information list is updated based on the filtering criteria.
        """
        key_0, key_1 = [key, ""]
        if nested_key:
            try:
                key_0, key_1 = key.split(key_splitter)
            except ValueError:
                raise NestedKeyException("Nested key must be in the format <key><key_splitter><nested_key>.")
            if self._streams_info and (
                key_0 not in self._streams_info[0] or key_1 not in self._streams_info[0][key_0]
            ):
                raise KeyNotFoundException(f"Nested key '{key}' is not present in the streams.")
        elif self._streams_info and key not in self._streams_info[0]:
            raise KeyNotFoundException(f"Key '{key}' is not present in the streams.")
        if not isinstance(filters, list):
            filters = [filters]
        any_or_all = any if retrieve else all
        not_operator = lambda x: x if retrieve else not x

        def check_filter(stream_info, fltr):
            value = stream_info.get(key_0, {}).get(key_1) if nested_key else stream_info.get(key)
            logger.info(f"Filter: {fltr}, Value: {value}")
            # Case 1: Both filter and value are None, return True
            if fltr is None and value is None:
                return True

            # Case 2: Filter is None, but value is not None, return False
            if fltr is None and value is not None:
                return False

            # Case 3: Filter is not None, but value is None, return False
            if fltr is not None and value is None:
                return False

            # Case 4: Both filter and value are not None, apply the filter condition
            if isinstance(fltr, bool):
                return value == fltr
            if isinstance(fltr, str):
                return re.search(re.compile(fltr, flags=re.IGNORECASE), str(value)) is not None

            # Case 5: Invalid filter type, return False
            return False

        self._streams_info = list(
            filter(
                lambda stream_info: any_or_all(not_operator(check_filter(stream_info, fltr)) for fltr in filters),
                self._streams_info,
            )
        )

    def reset_operations(self):
        """
        Reset the internal streams information list to its initial state before various operations were applied.

        Resets the streams information list to its original state before any filtering, sorting, or other operations were performed.
        The original parsed streams information is restored for further operations.

        Returns:
            None: The internal streams information list is reset to its initial state.
        """
        self._streams_info = self._streams_info_backup.copy()

    def remove_by_extension(self, extensions: Union[str, list[str]]):
        """
        Remove stream information with specific file extension(s).

        Removes stream information from the internal streams information list based on the provided file extension(s).
        If the stream URL ends with the specified extension(s), it will be removed from the list.

        Args:
            - `extensions` (Union[str, list[str]]): File extension or list of file extensions to be removed from the streams information.

        Returns:
            None: The internal streams information list is updated, removing streams with the specified extension(s).
        """
        self.filter_by("url", extensions, retrieve=False)

    def retrieve_by_extension(self, extensions: Union[str, list[str]]):
        """
        Retrieve streams information with specific file extension(s).

        Retrieves stream information from the internal streams information list based on the provided file extension(s).
        Only streams with URLs ending with the specified extension(s) will be retained in the list.

        Args:
            - `extensions` (Union[str, list[str]]): File extension or list of file extensions to be retrieved from the streams information.

        Returns:
            None: The internal streams information list is updated, retaining only streams with the specified extension(s).
        """
        self.filter_by("url", extensions)

    def remove_by_category(self, categories: Union[str, list[str]]):
        """
        Remove streams information with specific categories.

        Removes stream information from the internal streams information list based on the provided categories.
        If the category of a stream contains the provided categories, that stream will be removed from the list.

        Args:
            - `categories` (Union[str, list[str]]): Category or list of categories to be removed from the streams information.

        Returns:
            None: The internal streams information list is updated, removing streams with specified categories.
        """
        self.filter_by("category", categories, retrieve=False)

    def retrieve_by_category(self, categories: Union[str, list[str]]):
        """
        Retrieve streams information with specific categories.

        Retrieves stream information from the internal streams information list based on the provided categories.
        Only streams containing the provided categories will be retained in the list.

        Args:
            - `categories` (Union[str, list[str]]): Category or list of categories to be retrieved from the streams information.

        Returns:
            None: The internal streams information list is updated, retaining only streams with specified categories.
        """
        self.filter_by("category", categories)

    def sort_by(
        self,
        key: str,
        key_splitter: str = "-",
        asc: bool = True,
        nested_key: bool = False,
    ):
        """
        Sorts the internal streams information list based on a specific key.

        Sorts the streams information list based on the provided key in ascending or descending order,
        according to the specified configuration options.

        Args:
            - `key` (str): The key to sort by. It can be a nested key separated by a splitter if 'nested_key' is True in config.
            - `key_splitter` (str): A string used to split nested keys (default is "-").
            - `asc` (bool): Indicates whether to sort in ascending (True) or descending (False) order (default is True).
            - `nested_key` (bool): Indicates whether the sort key is nested or not (default is False).

        Raises:
            - `NestedKeyException`: Raised if 'nested_key' is True but the key is not in the correct format.
            - `KeyNotFoundException`: Raised if Key is not found.

        Returns:
            None: The internal streams information list is sorted based on the specified key and configuration.
        """
        key_0, key_1 = [key, ""]
        if nested_key:
            try:
                key_0, key_1 = key.split(key_splitter)
            except ValueError:
                raise NestedKeyException("Nested key must be in the format <key><key_splitter><nested_key>.")
            if self._streams_info and (
                key_0 not in self._streams_info[0] or key_1 not in self._streams_info[0][key_0]
            ):
                raise KeyNotFoundException(f"Nested key '{key}' is not present in the streams.")
        elif self._streams_info and key not in self._streams_info[0]:
            raise KeyNotFoundException(f"Key '{key}' is not present in the streams.")

        self._streams_info = sorted(
            self._streams_info,
            key=lambda stream_info: (stream_info[key_0][key_1] is not None, stream_info[key_0][key_1])
            if nested_key
            else (stream_info[key] is not None, stream_info[key]),
            reverse=not asc,
        )

    def remove_duplicates(self, name: str = None, url: str = None):
        """
        Removes duplicate stream entries based on the provided 'name' pattern and exact 'url' match or
        remove all duplicates if name and url is not provided.

        Args:
            - `name` (str, optional): The name pattern to filter duplicates. Defaults to None.
            - `url` (str, optional): The exact URL to filter duplicates. Defaults to None.

        Returns:
            - `self`: The modified object after removing duplicate stream entries.
        """
        if name is None and url is not None:
            raise ParamNotPassedException(f"Param name is not passed.")

        if name is not None and url is None:
            raise ParamNotPassedException(f"Param url is not passed.")

        filtered_streams = []
        seen_entries = set()

        name_pattern = re.compile(name, re.IGNORECASE) if name else None

        for stream_info in self._streams_info:
            stream_name = stream_info.get("name")
            stream_url = stream_info.get("url")

            both_none = name is None and url is None

            if (
                (stream_name is not None and name_pattern is not None and re.search(name_pattern, stream_name))
                and (stream_url is not None and stream_url.lower() == url.lower())
            ) or both_none:
                is_found = False
                unique_key = (stream_name.lower(), stream_url.lower())

                if both_none:
                    is_found = unique_key in seen_entries
                else:
                    for seen_name, seen_url in seen_entries:
                        if re.search(name_pattern, seen_name) and seen_url == stream_url.lower():
                            is_found = True
                            break

                if not is_found:
                    seen_entries.add(unique_key)
                    filtered_streams.append(stream_info)
            else:
                filtered_streams.append(stream_info)

        self._streams_info = filtered_streams

        return self

    def get_json(self, indent: int = 4):
        """
        Get the streams information as a JSON string.

        Converts the internal streams information list into a JSON string representation
        with optional indentation for readability.

        Args:
            - `indent` (int, optional): Number of spaces for JSON indentation. Defaults to 4.

        Returns:
            str: JSON string representation of the internal streams information list.
        """
        return json.dumps(self._streams_info, indent=indent)

    def get_list(self):
        """
        Get the parsed streams information list.

        Returns the internal streams information list that has been parsed, filtered, and processed
        based on various operations performed on the original data source.

        Returns:
            list: Parsed streams information list containing dictionaries of stream details.
        """
        return self._streams_info

    def get_random_stream(self, random_shuffle: bool = True):
        """
        Return a random stream information.

        Retrieves a randomly selected stream information from the internal streams information list.
        Optionally, shuffles the list before selecting to provide a truly random choice.

        Args:
            - `random_shuffle` (bool, optional): Whether to shuffle the streams information list before selecting. Defaults to True.

        Returns:
            dict or None: A randomly selected stream information dictionary, or None if no streams are available.
        """
        if not len(self._streams_info):
            raise NoStreamsException("No streams information so could not get any random stream.")
        if random_shuffle:
            random.shuffle(self._streams_info)
        return random.choice(self._streams_info)

    def to_file(self, filename: str, format: str = "json"):
        """
        Save the parsed streams information to a file (CSV, JSON, or M3U).

        Saves the internal streams information list as a CSV, JSON, or M3U file with the specified filename and format.
        The format is determined by the file extension or the optional 'format' parameter.

        Args:
            - `filename` (str): Name of the file to save the streams information as.
            - `format` (str, optional): File format to save the streams information as (csv/json/m3u). Defaults to "json".

        Returns:
            None: The streams information is saved to the specified file in the specified format.
        """
        format = filename.split(".")[-1] if len(filename.split(".")) > 1 else format

        def with_extension(name, ext):
            name, ext = name.lower(), ext.lower()
            if ext in name:
                return name
            else:
                return name + ".%s" % ext

        filename = with_extension(filename, format)
        if len(self._streams_info) == 0:
            raise NoStreamsException("Either parsing is not done or no stream info was found after parsing.")
        logger.info("Saving to file: %s" % filename)
        if format == "json":
            data = json.dumps(self._streams_info, indent=4)
            with open(filename, mode="w", encoding="utf-8") as fp:
                fp.write(data)
            logger.info("Saved to file: %s" % filename)

        elif format == "csv":
            if self._enforce_schema:
                ndict_to_csv(self._streams_info, filename)
                logger.info("Saved to file: %s" % filename)
            else:
                raise SavingNotSupportedException(
                    "Saving to csv file not supported if the schema was not forced (enforce_schema)."
                )

        elif format == "m3u":
            content = self._get_m3u_content(self._streams_info)
            with open(filename, mode="w", encoding="utf-8") as fp:
                fp.write(content)
            logger.info("Saved to file: %s" % filename)
        else:
            raise UnrecognizedFormatException("Unrecognised format.")
