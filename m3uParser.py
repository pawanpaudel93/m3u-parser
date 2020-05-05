import csv
import json
import os
import re
from random import random

import requests


def is_present(regex, content):
    match = re.search(re.compile(regex, flags=re.IGNORECASE), content)
    return match.group(1) or ""


class M3uParser:

    def __init__(self):
        self.files = []
        self.lines = []
        self.content = ""

    # Download the file from the given url
    def download_m3u(self, url):
        try:
            self.content = requests.get(url).text
        except:
            print("Cannot parse anything from the url!!!")
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
        lineInfo = self.lines[n]
        lineLink = self.lines[n + 1]
        if lineInfo != "#EXTM3U":
            try:
                name = is_present(r"tvg-name=\"(.*?)\"", lineInfo)
                tid = is_present(r"tvg-id=\"(.*?)\"", lineInfo)
                logo = is_present(r"tvg-logo=\"(.*?)\"", lineInfo)
                group = is_present(r"group-title=\"(.*?)\"", lineInfo)
                title = is_present("[,](?!.*[,])(.*?)$", lineInfo)
                country = is_present(r"tvg-country=\"(.*?)\"", lineInfo)
                language = is_present(r"tvg-language=\"(.*?)\"", lineInfo)
                # ~ print(name+"||"+id+"||"+logo+"||"+group+"||"+title)

                test = {
                    "title": title,
                    "tvg-name": name,
                    "tvg-id": tid,
                    "tvg-logo": logo,
                    "tvg-group": group,
                    "tvg-country": country,
                    "tvg-language": language,
                    "titleFile": os.path.basename(lineLink),
                    "link": lineLink
                }
                self.files.append(test)
            except AttributeError:
                pass

    # Remove files with a certain file extension
    def remove_files_extension(self, extension):
        matches = [extension.lower(), extension.upper()]
        self.files = list(filter(lambda file: all([ext not in file["titleFile"] for ext in matches]), self.files))
        # Select only files with a certain file extension

    def retrieve_files_extension(self, extension):
        # Use the extension as list
        if not isinstance(extension, list):
            extension = [extension]
        if not len(extension):
            print("No filter in based on extensions")
            return
        new = []
        # Iterate over all files and extensions
        for file in self.files:
            for ext in extension:
                matches = [ext.upper(), ext.lower()]
                if any([ext in file["titleFile"] for ext in matches]):
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        print("Filter in based on extension: [" + ",".join(extension) + "]")
        self.files = new

    # Remove files that contains a certain filterWord
    def remove_files_grpname(self, filter_word):
        self.files = list(filter(
            lambda file: filter_word.lower() not in file["tvg-group"] or filter_word.upper() not in file[
                "tvg-group"], self.files))

    # Select only files that contains a certain filterWord
    def retrieve_files_grpname(self, filter_word):
        # Use the filter words as list
        if not isinstance(filter_word, list):
            filter_word = [filter_word]
        if not len(filter_word):
            print("No filter in based on groups")
            return
        new = []
        for file in self.files:
            for fw in filter_word:
                if fw in file["tvg-group"]:
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        print("Filter in based on groups: [" + ",".join(filter_word) + "]")
        self.files = new

    # Getter for the list
    def get_list(self):
        return json.dumps(self.files, indent=4)

    # Return the info assciated to a certain file name
    def get_custom_title(self, original_name):
        result = list(filter(lambda file: file["titleFile"] == original_name, self.files))
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
    url = "https://iptv-org.github.io/iptv/categories/health.m3u"
    myFile.download_m3u(url)
    # myFile.remove_files_extension('m3u8')
    print(myFile.get_list())
