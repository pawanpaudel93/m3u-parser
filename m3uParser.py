import csv
import json
import os
import re
import urllib3
from random import random
from urllib.parse import urlparse


def is_present(regex, content):
    match = re.search(re.compile(regex, flags=re.IGNORECASE), content)
    return match.group(1) or ""


def to_json(files):
    return json.dumps(files, indent=4)


class M3uParser:

    def __init__(self):
        self.files = []
        self.lines = []
        self.content = ""

    # Download the file from the given url
    def parse_m3u(self, url):
        if urlparse(url).scheme != '' or 'www' in url:
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
        self.read_m3u()

    # Read the file from the given path
    def read_m3u(self):
        if self.read_all_lines() > 0:
            self.parse_file()
        else:
            print("No content to parse!!!")

    # Read all file lines
    def read_all_lines(self):
        self.lines = [line.rstrip('\n') for line in self.content.split("\n") if line != '']
        return len(self.lines)

    def parse_file(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                self.manage_line(n)

    def manage_line(self, n):
        line_info = self.lines[n]
        line_link = self.lines[n + 1]
        if line_info != "#EXTM3U":
            try:
                name = is_present(r"tvg-name=\"(.*?)\"", line_info)
                tid = is_present(r"tvg-id=\"(.*?)\"", line_info)
                logo = is_present(r"tvg-logo=\"(.*?)\"", line_info)
                group = is_present(r"group-title=\"(.*?)\"", line_info)
                title = is_present("[,](?!.*[,])(.*?)$", line_info)
                country = is_present(r"tvg-country=\"(.*?)\"", line_info)
                language = is_present(r"tvg-language=\"(.*?)\"", line_info)

                self.files.append({
                    "title": title,
                    "tvg-name": name,
                    "tvg-id": tid,
                    "tvg-logo": logo,
                    "tvg-group": group,
                    "tvg-country": country,
                    "tvg-language": language,
                    "title-file": os.path.basename(line_link),
                    "link": line_link
                })
            except AttributeError:
                pass

    def filter_by(self, key, filters, jsonify=False, retrieve=True):
        if not filters:
            print("Filter word/s missing!!!")
            return
        if not isinstance(filters, list):
            filters = [filters]
        if retrieve:
            files = list(filter(
                lambda file: any([re.search(re.compile(fltr, flags=re.IGNORECASE), file[key]) for fltr in filters]),
                self.files))
        else:
            files = list(filter(
                lambda file: any([not re.search(re.compile(fltr, flags=re.IGNORECASE), file[key]) for fltr in filters]),
                self.files))
        if jsonify:
            files = to_json(files)
        return files

    # Remove files with a certain file extension
    def remove_by_extension(self, extension, jsonify=False):
        files = self.filter_by('title-file', extension, jsonify, retrieve=False)
        return files

    # Select only files with a certain file extension
    def retrieve_by_extension(self, extension, jsonify=False):
        files = self.filter_by('title-file', extension, jsonify, retrieve=True)
        return files

    # Remove files that contains a certain filterWord
    def remove_by_grpname(self, filter_word, jsonify=False):
        files = self.filter_by('tvg-group', filter_word, jsonify, retrieve=False)
        return files

    # Select only files that contains a certain filterWord
    def retrieve_by_grpname(self, filter_word, jsonify=False):
        files = self.filter_by('title-file', filter_word, jsonify, retrieve=True)
        return files

    def sort_by(self, key, jsonify=False, asc=True):
        files = sorted(self.files, key=lambda file: file[key], reverse=not asc)
        if jsonify:
            files = to_json(files)
        return files

    # Getter for the list
    def get_json(self):
        return json.dumps(self.files, indent=4)

    # Return the info assciated to a certain file name
    def get_custom_title(self, original_name):
        result = list(filter(lambda file: file["title-file"] == original_name, self.files))
        if len(result):
            return result
        else:
            print("No file corresponding to: " + original_name)

    # Return a random element
    def get_file(self, random_shuffle):
        if random_shuffle:
            random.shuffle(self.files)
        if not len(self.files):
            print("No files in the array, cannot extract anything")
            return None
        return self.files.pop()

    def to_file(self, filename, format='json'):
        def with_extension(name, ext):
            splits = name.split('.')
            if len(splits) > 1 and ext not in splits:
                splits[-1] = ext
                name = '.'.join(splits)
            if ext in name:
                return name
            else:
                return name + ext

        if format == 'json':
            data = json.dumps(self.files, indent=4)
            with open(with_extension(filename, format), 'w') as fp:
                fp.write(data)

        elif format == 'csv':
            keys = self.files[0].keys()
            with open(with_extension(filename, format), 'w') as fp:
                w = csv.DictWriter(fp, keys)
                w.writeheader()
                w.writerows(self.files)
        else:
            print("Unrecognised format!!!")


def get_absolute_path(path):
    if not os.path.isabs(path):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(currentDir, path)
    return path


if __name__ == "__main__":
    myFile = M3uParser()
    url = "https://iptv-org.github.io/iptv/index.country.m3u"
    myFile.parse_m3u(url)
    files1 = myFile.filter_by('title-file', 'flv')
    files2 = myFile.retrieve_by_extension('flv')
    print(files1 == files2)
    files3 = myFile.sort_by('tvg-group')
    print(to_json(files3))
    # myFile.remove_files_extension('m3u8')
    # myFile.remove_files_grpname('Zimbabwe')
    # print(myFile.get_json())
