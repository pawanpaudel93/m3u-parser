import csv
import json
import os
import re
import urllib3
from random import random
from urllib.parse import urlparse
import pycountry


def is_present(regex, content):
    match = re.search(re.compile(regex, flags=re.IGNORECASE), content)
    return match.group(1) if match else ""


class M3uParser:

    def __init__(self):
        self.files = []
        self.lines = []
        self.content = ""
        self.url_regex = r"\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([" \
                         r"^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\"\\\/.," \
                         r"<>?\xab\xbb\u201c\u201d\u2018\u2019])) "

    # Download the file from the given url
    def parse_m3u(self, url):
        if urlparse(url).scheme != '' or re.search(re.compile(self.url_regex), url):
            try:
                with urllib3.PoolManager() as http:
                    self.content = http.request('GET', url).data.decode('utf-8')
            except:
                print("Cannot read anything from the url!!!")
                exit()
        else:
            try:
                with open(url) as fp:
                    self.content = fp.read()
            except FileNotFoundError:
                print("File doesn't exist!!!")
                exit()
        self.__read_m3u()

    # Read the file from the given path
    def __read_m3u(self):
        if self.__read_all_lines() > 0:
            self.__parse_file()
        else:
            print("No content to parse!!!")

    # Read all file lines
    def __read_all_lines(self):
        self.lines = [line.rstrip('\n') for line in self.content.split("\n") if line != '']
        return len(self.lines)

    def __parse_file(self):
        num_line = len(self.lines)
        for n in range(num_line):
            line = self.lines[n]
            if "#EXTINF" in line:
                self.__manage_line(n)

    def __manage_line(self, n):
        line_info = self.lines[n]
        line_link = self.lines[n + 1]
        if line_info and re.search(re.compile(self.url_regex), line_link):
            try:
                tvg_name = is_present(r"tvg-name=\"(.*?)\"", line_info)
                tvg_id = is_present(r"tvg-id=\"(.*?)\"", line_info)
                logo = is_present(r"tvg-logo=\"(.*?)\"", line_info)
                group = is_present(r"group-title=\"(.*?)\"", line_info)
                title = is_present("[,](?!.*[,])(.*?)$", line_info)
                country = is_present(r"tvg-country=\"(.*?)\"", line_info)
                language = is_present(r"tvg-language=\"(.*?)\"", line_info)
                tvg_url = is_present(r"tvg-url=\"(.*?)\"", line_info)

                self.files.append({
                    "name": title,
                    "logo": logo,
                    "url": line_link,
                    "category": group,
                    "language": {
                        "code": pycountry.languages.get(name=country.capitalize()).alpha_3,
                        "name": language,
                    },
                    "country": {
                        "code": country,
                        "name": pycountry.countries.get(alpha_2=country.upper()).name
                    },
                    "tvg": {
                        "id": tvg_id,
                        "name": tvg_name,
                        "url": tvg_url,
                    }
                })
            except AttributeError:
                pass

    def filter_by(self, key, filters, retrieve=True):
        if not filters:
            print("Filter word/s missing!!!")
            return
        if not isinstance(filters, list):
            filters = [filters]
        if retrieve:
            self.files = list(filter(
                lambda file: any([re.search(re.compile(fltr, flags=re.IGNORECASE), file[key]) for fltr in filters]),
                self.files))
        else:
            self.files = list(filter(
                lambda file: any([not re.search(re.compile(fltr, flags=re.IGNORECASE), file[key]) for fltr in filters]),
                self.files))

    # Remove files with a certain file extension
    def remove_by_extension(self, extension):
        self.filter_by('url', extension, retrieve=False)

    # Select only files with a certain file extension
    def retrieve_by_extension(self, extension):
        self.filter_by('url', extension, retrieve=True)

    # Remove files that contains a certain filterWord
    def remove_by_grpname(self, filter_word):
        self.filter_by('category', filter_word, retrieve=False)

    # Select only files that contains a certain filterWord
    def retrieve_by_grpname(self, filter_word):
        self.filter_by('category', filter_word, retrieve=True)

    def sort_by(self, key, jsonify=False, asc=True):
        self.files = sorted(self.files, key=lambda file: file[key], reverse=not asc)

    # Getter for the list
    def get_json(self):
        return json.dumps(self.files, indent=4)

    def get_dict(self):
        return self.files

    # Return a random element
    def get_file(self, random_shuffle):
        if random_shuffle:
            random.shuffle(self.files)
        if not len(self.files):
            print("No files in the array, cannot extract anything")
            return None
        return self.files.pop()

    def to_file(self, filename, format='json'):
        format = filename.split('.')[-1] if len(filename.split('.')) > 1 else format

        def with_extension(name, ext):
            name, ext = name.lower(), ext.lower()
            if ext in name:
                return name
            else:
                return name + f".{ext}"

        if format == 'json':
            data = json.dumps(self.files, indent=4)
            with open(with_extension(filename, format), 'w') as fp:
                fp.write(data)

        elif format == 'csv':
            ndict_to_csv(self.files, with_extension(filename, format))
        else:
            print("Unrecognised format!!!")


def is_dict(item, ans=None):
    if ans is None:
        ans = []
    tree = []
    for k, v in item.items():
        if isinstance(v, dict):
            ans.append(str(k))
            tree.extend(is_dict(v, ans))
            ans = []
        else:
            if ans:
                ans.append(str(k))
                key = ','.join(ans).replace(',', '_')
                tree.extend([(key, str(v))])
                ans.remove(str(k))
            else:
                tree.extend([(str(k), str(v))])
    return tree


def get_tree(item):
    tree = []
    if isinstance(item, dict):
        tree.extend(is_dict(item, ans=[]))
    elif isinstance(item, list):
        tree = []
        for i in item:
            tree.append(get_tree(i))
    return tree


def render_csv(header, data, out_path='output.csv'):
    input = []
    with open(out_path, 'w') as f:
        dict_writer = csv.DictWriter(f, fieldnames=header)
        dict_writer.writeheader()
        if not isinstance(data[0], list):
            input.append(dict(data))
        else:
            for i in data:
                input.append(dict(i))
        dict_writer.writerows(input)
    return


def ndict_to_csv(obj, output_path):
    tree = get_tree(obj)
    if isinstance(obj, list):
        header = [i[0] for i in tree[0]]
    else:
        header = [i[0] for i in tree]
    return render_csv(header, tree, output_path)


if __name__ == "__main__":
    myFile = M3uParser()
    url = "https://iptv-org.github.io/iptv/languages/spa.m3u"
    myFile.parse_m3u(url)
    # myFile.remove_by_extension('m3u8')
    # myFile.remove_by_grpname('Zimbabwe')
    # myFile.filter_by('tvg-language', 'Hungarian', retrieve=False)
    print(len(myFile.get_dict()))
    # myFile.to_file('pawan.csv')
