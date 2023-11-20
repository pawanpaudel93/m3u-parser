# m3u_parser

![version](https://img.shields.io/badge/version-0.3.0-blue.svg?cacheSeconds=2592000)

A Python package for parsing m3u files and extracting streams information. The package allows you to convert the parsed information into JSON or CSV format and provides various filtering and sorting options.

## Install

Using pip,

```sh
pip install m3u-parser
```

Or using pipenv,

```sh
pipenv install m3u-parser
```

## Usage

Here is an example of how to use the M3uParser class:

```python
from m3u_parser import M3uParser

url = "/home/pawan/Downloads/ru.m3u"
useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

# Instantiate the parser
parser = M3uParser(timeout=5, useragent=useragent)

# Parse the m3u file
parser.parse_m3u(url)

# Remove by mp4 extension
parser.remove_by_extension('mp4')

# Filter streams by status
parser.filter_by('status', 'GOOD')

# Get the list of streams
print(len(parser.get_list()))

# Convert streams to JSON and save to a file
parser.to_file('streams.json')
```

## API Reference

`M3uParser`
The main class that provides the functionality to parse m3u files and manipulate the streams information.

### Initialization

```python
parser = M3uParser(useragent=default_useragent, timeout=5)
```

- `useragent` (optional): User agent string for HTTP requests. Default is a Chrome User-Agent string.
- `timeout` (optional): Timeout duration for HTTP requests in seconds. Defaults to `5`.

### Methods

#### parse_m3u

`parse_m3u(data_source: str,
    schemes=['http', 'https', 'ftp', 'ftps'],
    status_checker=dict(),
    check_live=True,
    enforce_schema=True) -> M3uParser`

Parses the content of a local file or URL and extracts the streams information.

- `data_source`: The path to the m3u file, which can be a local file path or a URL.
- `schemes` (list, optional): A list of allowed URL schemes. Default is `["http", "https", "ftp", "ftps"]`.
- `status_checker` (dict, optional): A dictionary mapping URL schemes to custom status checker functions. Default is `dict()`.
- `check_live` (bool, optional): Indicates whether to check the status of live streams (default is `True`).
- `enforce_schema` (bool, optional): Indicates whether to enforce a specific schema for parsed data.
    If enforced, non-existing fields in a stream are filled with None/null.
    If not enforced, non-existing fields are ignored. Default is `True`.

You can define your own custom status checker function for schemes. If no status checker is defined, then the default status checker is used. The default status checker works for `http` and `https` url schemes only.

```python
async def ftp_checker(url: str) -> bool:
    # Checker implementation
    # Return either True for good status or False for bad status
    return True

parser.parse_m3u(path, schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)
```

#### parse_json

`parse_json(data_source: str,
    schemes=['http', 'https', 'ftp', 'ftps'],
    status_checker=dict(),
    check_live=True,
    enforce_schema=True) -> M3uParser`

Parses the content of a local file or URL and extracts the streams information.

- `data_source`: The path to the json file, which can be a local file path or a URL.
- `schemes` (list, optional): A list of allowed URL schemes. Default is `["http", "https", "ftp", "ftps"]`.
- `status_checker` (dict, optional): A dictionary mapping URL schemes to custom status checker functions. Default is `dict()`.
- `check_live` (bool, optional): Indicates whether to check the status of live streams (default is `True`).
- `enforce_schema` (bool, optional): Indicates whether to enforce a specific schema for parsed data.
    If enforced, non-existing fields in a stream are filled with None/null.
    If not enforced, non-existing fields are ignored. Default is `True`.

You can define your own custom status checker function for schemes. If no status checker is defined, then the default status checker is used. The default status checker works for `http` and `https` url schemes only.

```python
async def ftp_checker(url: str) -> bool:
    # Checker implementation
    # Return either True for good status or False for bad status
    return True

parser.parse_json(path, schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)
```

#### parse_csv

`parse_csv(data_source: str,
    schemes=['http', 'https', 'ftp', 'ftps'],
    status_checker=dict(),
    check_live=True,
    enforce_schema=True) -> M3uParser`

Parses the content of a local file or URL and extracts the streams information.

- `data_source`: The path to the csv file, which can be a local file path or a URL.
- `schemes` (list, optional): A list of allowed URL schemes. Default is `["http", "https", "ftp", "ftps"]`.
- `status_checker` (dict, optional): A dictionary mapping URL schemes to custom status checker functions. Default is `dict()`.
- `check_live` (bool, optional): Indicates whether to check the status of live streams (default is `True`).
- `enforce_schema` (bool, optional): Indicates whether to enforce a specific schema for parsed data.
    If enforced, non-existing fields in a stream are filled with None/null.
    If not enforced, non-existing fields are ignored. Default is `True`.

You can define your own custom status checker function for schemes. If no status checker is defined, then the default status checker is used. The default status checker works for `http` and `https` url schemes only.

```python
async def ftp_checker(url: str) -> bool:
    # Checker implementation
    # Return either True for good status or False for bad status
    return True

parser.parse_csv(path, schemes=['http', 'https', 'ftp'], status_checker={"ftp": ftp_checker}, check_live=True, enforce_schema=True)
```

#### filter_by

`filter_by(key: str, filters: Union[str, list[Union[str, None, bool]], None, bool], key_splitter: str = "-", retrieve: bool = True, nested_key: bool = False,) -> M3uParser`

Filters the streams information based on a key and filter/s.

- `key`: The key to filter on, can be a single key or nested key (e.g., "language-name").
- `filters`: The filter word/s to perform the filtering operation.
- `key_splitter` (str, optional): A string used to split nested keys (default is `"-"`).
- `retrieve` (bool, optional): Indicates whether to retrieve or remove based on the filter key (default is `True`).
- `nested_key` (bool, optional): Indicates whether the filter key is nested or not (default is `False`).

```python
parser.filter_by(key, filters, key_splitter="-", retrieve=True, nested_key=False)
```

#### reset_operations

`reset_operations() -> M3uParser`

Resets the streams information list to the initial state before any filtering or sorting operations.

```python
parser.reset_operations()
```

#### remove_by_extension

`remove_by_extension(extensions: Union[str, list[str]]) -> M3uParser`

Removes stream information with a certain extension(s).

- `extensions`: The name of the extension(s) to remove, e.g., "mp4" or ["mp4", "m3u8"].

```python
parser.remove_by_extension(extensions)
```

#### retrieve_by_extension

`retrieve_by_extension(extension: Union[str, list[str]]) -> M3uParser`

Retrieves only stream information with a certain extension(s).

- `extensions`: The name of the extension(s) to retrieve, e.g., "mp4" or ["mp4", "m3u8"].

```python
parser.retrieve_by_extension(extensions)
```

#### remove_by_category

`remove_by_category(categories: Union[str, list[str]]) -> M3uParser`

Removes stream information containing certain categories.

- `categories`: Category or list of categories to be removed from the streams information

```python
parser.remove_by_category(categories)
```

#### retrieve_by_category

`retrieve_by_category(categories: Union[str, list[str]]) -> M3uParser`

Selects only stream information containing certain categories.

- `categories`: Category or list of categories to be retrieved from the streams information.

```python
parser.retrieve_by_category(categories)
```

#### sort_by

`sort_by(key: str, key_splitter: str = "-", asc: bool = True, nested_key: bool = False) -> M3uParser`

Sorts the streams information based on a key in ascending or descending order.

- `key`: The key to sort on, can be a single key or nested key seperated by `key_splitter` (e.g., "language-name").
- `key_splitter` (str, optional): A string used to split nested keys (default is `"-"`).
- `asc` (bool, optional): Indicates whether to sort in ascending (True) or descending (False) order (default is `True`).
- `nested_key` (bool, optional): Indicates whether the sort key is nested or not (default is `False`).

```python
parser.sort_by(key, key_splitter="-", asc=True, nested_key=False)
```

#### remove_duplicates

`remove_duplicates(self, name: str = None, url: str = None) -> M3uParser`

Removes duplicate stream entries based on the provided 'name' pattern and exact 'url' match or remove all duplicates if name and url is not provided.
  
- `name` (str, optional): The name pattern to filter duplicates. Defaults to `None`.
- `url` (str, optional): The exact URL to filter duplicates. Defaults to `None`.

```python
parser.remove_duplicates()
# or
parser.remove_duplicates("Channel 1", "http://example.com/stream1")
```

### get_json

`get_json(indent: int = 4) -> str`

Returns the streams information in JSON format.

- indent (optional): If `indent` is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines.

```python
json_data = parser.get_json(indent)
```

### get_list

`get_list() -> list`

Returns the list of streams information after any filtering or sorting operations.

```python
streams = parser.get_list()
```

### to_file

`to_file(filename: str, format: str = "json") -> str`

Saves the streams information to a file in the specified format.

- `filename`: The name of the output file.
- `format` (optional): The output file format, either "json" or "csv". Default is `"json"`.

```python
parser.to_file(filename, format="json")
```

## Other Implementations

- `Golang`: [go-m3u-parser](https://github.com/pawanpaudel93/go-m3u-parser)
- `Rust`: [rs-m3u-parser](https://github.com/pawanpaudel93/rs-m3u-parser)
- `Typescript`: [ts-m3u-parser](https://github.com/pawanpaudel93/ts-m3u-parser)

## Author

👤 **Pawan Paudel**

- Github: [@pawanpaudel93](https://github.com/pawanpaudel93)

## 🤝 Contributing

Contributions, issues and feature requests are welcome! \ Feel free to check [issues page](https://github.com/pawanpaudel93/m3u_parser/issues).

## Show your support

Give a ⭐️ if this project helped you!

Copyright © 2020 [Pawan Paudel](https://github.com/pawanpaudel93).
