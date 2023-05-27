# m3u_parser

![version](https://img.shields.io/badge/version-0.2.0-blue.svg?cacheSeconds=2592000)

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
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"

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
parser = M3uParser(useragent=None, timeout=5)
```

- `useragent` (optional): The User-Agent string to use for HTTP requests. Default is a Chrome User-Agent string.
- `timeout` (optional): The timeout value in seconds for HTTP requests. Default is 5 seconds.

### Methods

#### parse_m3u

`parse_m3u(path: str, check_live: bool = True, enforce_schema: bool = True) -> None`

Parses the content of a local file or URL and extracts the streams information.

- `path`: The path to the m3u file, which can be a local file path or a URL.
- `check_live` (optional): Set to `True` to check if the stream links are working or not. Default is `True`.
- `enforce_schema` (optional): If `True`, non-existing fields in a stream are filled with None. If `False`, non-existing fields are ignored. Default is `True`.

```python
parser.parse_m3u(path, check_live=True, enforce_schema=True)
```

#### filter_by

`filter_by(key: str, filters: Union[str, list], key_splitter: str = "-", retrieve: bool = True, nested_key: bool = False) -> None`

Filters the streams information based on a key and filter/s.

- `key`: The key to filter on, can be a single key or nested key (e.g., "language-name").
- `filters`: The filter word/s to perform the filtering operation.
- `key_splitter` (optional): A splitter to split the nested keys. Default is "-".
- `retrieve` (optional): Set to `True` to retrieve matching streams or `False` to remove matching streams. Default is `True`.
- `nested_key` (optional): Set to `True` if the key is nested or `False` if it's not. Default is `False`.

```python
parser.filter_by(key, filters, key_splitter="-", retrieve=True, nested_key=False)
```

#### reset_operations

`reset_operations() -> None`

Resets the streams information list to the initial state before any filtering or sorting operations.

```python
parser.reset_operations()
```

#### remove_by_extension

`remove_by_extension(extension: Union[str, list]) -> None`

Removes stream information with a certain extension or extensions.

- `extension`: The name of the extension(s) to remove, e.g., "mp4" or ["mp4", "m3u8"].

```python
parser.remove_by_extension(extension)
```

#### retrieve_by_extension

`retrieve_by_extension(extension: Union[str, list]) -> None`

Retrieves only stream information with a certain extension or extensions.

- `extension`: The name of the extension(s) to retrieve, e.g., "mp4" or ["mp4", "m3u8"].

```python
parser.retrieve_by_extension(extension)
```

#### remove_by_category

`remove_by_category(filter_word: Union[str, list]) -> None`

Removes stream information with a category containing certain filter word/s.

- `filter_word`: The filter word/s to match against the category. It can be a string or a list of filter word/s.

```python
parser.remove_by_category(filter_word)
```

#### retrieve_by_category

`retrieve_by_category(filter_word: Union[str, list]) -> None`

Selects only stream information with a category containing certain filter word/s.

- `filter_word`: The filter word/s to match against the category. It can be a string or a list of filter word/s.

```python
parser.retrieve_by_category(filter_word)
```

#### sort_by

`sort_by(key: str, key_splitter: str = "-", asc: bool = True, nested_key: bool = False) -> None`

Sorts the streams information based on a key in ascending or descending order.

- `key`: The key to sort on, can be a single key or nested key seperated by `key_splitter` (e.g., "language-name").
- `key_splitter` (optional): A splitter used to split nested keys. Default is "-".
- `asc` (optional): Set to `True` to sort in descending order, or `False` to sort in ascending order. Default is `False`.
- `nested_key` (optional): Set to `True` if the key is nested or `False` if it's not. Default is `False`.

```python
parser.sort_by(key, key_splitter="-", asc=True, nested_key=False)
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

`to_file(filename: str, format: str = "json") -> None`

Saves the streams information to a file in the specified format.

- `filename`: The name of the output file.
- `format` (optional): The output file format, either "json" or "csv". Default is "json".

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
