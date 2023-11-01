import json
import os
import sys
from pathlib import Path

import pytest

file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))

from m3u_parser import FilterConfig, M3uParser, ParseConfig, SortConfig
from m3u_parser.exceptions import KeyNotFoundException, NoStreamsException

# Sample M3U content for testing
SAMPLE_M3U_CONTENT = """
#EXTM3U
#EXTINF:-1 tvg-id="Channel 1" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="NP" tvg-language="Newari" group-title="News",Channel 1
http://example.com/stream1
#EXTINF:-1 tvg-id="Channel 2" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="IN" tvg-language="Hindi" group-title="News",Channel 2
http://example.com/stream2
#EXTINF:-1 tvg-id="Channel 3" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="CN" tvg-language="Chinesee" group-title="News",Channel 3
http://example.com/stream3
#EXTINF:0,Dlf
#EXTVLCOPT:network-caching=1000
rtsp://10.0.0.1:554/?avm=1&freq=514&bw=8&msys=dvbc&mtype=256qam&sr=6900&specinv=0&pids=0,16,17,18,20,800,810,850
"""

SAMPLE_JSON_CONTENT = json.dumps(
    [
        {
            "name": "Channel 1",
            "logo": "https://i.imgur.com/AvCQYgu.png",
            "url": "http://example.com/stream1",
            "category": "News",
            "tvg": {"id": "Channel 1", "name": None, "url": None},
            "country": {"code": "NP", "name": "Nepal"},
            "language": {"code": "new", "name": "Newari"},
        },
        {
            "name": "Channel 2",
            "logo": "https://i.imgur.com/AvCQYgu.png",
            "url": "http://example.com/stream2",
            "category": "News",
            "tvg": {"id": "Channel 2", "name": None, "url": None},
            "country": {"code": "IN", "name": "India"},
            "language": {"code": "hin", "name": "Hindi"},
        },
        {
            "name": "Channel 3",
            "logo": "https://i.imgur.com/AvCQYgu.png",
            "url": "http://example.com/stream3",
            "category": "News",
            "tvg": {"id": "Channel 3", "name": None, "url": None},
            "country": {"code": "CN", "name": "China"},
            "language": {"code": None, "name": "Chinesee"},
        },
    ]
)

SAMPLE_CSV_CONTENT = """name,logo,url,category,tvg_id,tvg_name,tvg_url,country_code,country_name,language_code,language_name
Channel 1,https://i.imgur.com/AvCQYgu.png,http://example.com/stream1,News,Channel 1,,,NP,Nepal,new,Newari
Channel 2,https://i.imgur.com/AvCQYgu.png,http://example.com/stream2,News,Channel 2,,,IN,India,hin,Hindi
Channel 3,https://i.imgur.com/AvCQYgu.png,http://example.com/stream3,News,Channel 3,,,CN,China,,Chinesee
"""


async def rtsp_checker(url: str):
    return "GOOD"


# Fixture to create a temporary M3U file for testing
@pytest.fixture
def temp_m3u_file(tmpdir):
    m3u_file = tmpdir.join("test.m3u")
    with open(m3u_file, "w") as f:
        f.write(SAMPLE_M3U_CONTENT)
    return str(m3u_file)


# Fixture to create a temporary JSON file for testing
@pytest.fixture
def temp_json_file(tmpdir):
    json_file = tmpdir.join("test.json")
    with open(json_file, "w") as f:
        f.write((SAMPLE_JSON_CONTENT))
    return str(json_file)


# Fixture to create a temporary CSV file for testing
@pytest.fixture
def temp_csv_file(tmpdir):
    csv_file = tmpdir.join("test.csv")
    with open(csv_file, "w") as f:
        f.write((SAMPLE_CSV_CONTENT))
    return str(csv_file)


# Test M3uParser class
class TestM3uParser:
    # Test parsing of M3U content
    def test_parse_m3u(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        streams = parser.get_list()
        assert len(streams) == 3

    # Test parsing of M3U content
    def test_parse_m3u_with_schemes(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(
            temp_m3u_file,
            ParseConfig(check_live=True, schemes=["http", "https", "rtsp"], status_checker={"rtsp": rtsp_checker}),
        )
        streams = parser.get_list()
        assert len(streams) == 4

    def test_parse_json(self, temp_json_file):
        parser = M3uParser()
        parser.parse_json(temp_json_file, ParseConfig(check_live=False))
        streams = parser.get_list()
        assert len(streams) == 3

    def test_parse_csv(self, temp_csv_file):
        parser = M3uParser()
        parser.parse_csv(temp_csv_file, ParseConfig(check_live=False))
        streams = parser.get_list()
        assert len(streams) == 3

    # Test filtering by extension
    def test_filter_by_extension(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.retrieve_by_extension('mp4')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test filtering by nested key
    def test_filter_by_nested_key(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file)
        parser.filter_by('language.code', None, FilterConfig(key_splitter=".", retrieve=False, nested_key=True))
        streams = parser.get_list()
        assert len(streams) == 1

    # Test filtering by invalid category
    def test_filter_by_invalid_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.filter_by('category', 'Invalid')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test filtering by invalid category
    def test_filter_by_invalid_key(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        with pytest.raises(KeyNotFoundException):
            parser.filter_by('invalid', 'Invalid')

    # Test sorting by stream name in ascending order
    def test_sort_by_name_asc(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.sort_by('name')
        streams = parser.get_list()
        assert streams[0]['name'] == 'Channel 1'
        assert streams[1]['name'] == 'Channel 2'
        assert streams[2]['name'] == 'Channel 3'

    # Test sorting by stream name in descending order
    def test_sort_by_name_desc(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.sort_by('name', SortConfig(asc=False))
        streams = parser.get_list()
        assert streams[0]['name'] == 'Channel 3'
        assert streams[1]['name'] == 'Channel 2'
        assert streams[2]['name'] == 'Channel 1'

    # Test resetting operations
    def test_reset_operations(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.retrieve_by_extension('mp4')
        parser.reset_operations()
        streams = parser.get_list()
        assert len(streams) == 3

    # Test saving to JSON file
    def test_save_to_json(self, temp_m3u_file, tmpdir):
        json_file = tmpdir.join("output.json")
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.to_file(str(json_file), format="json")
        print(json_file)
        assert os.path.exists(str(json_file))

    # Test saving to CSV file
    def test_save_to_csv(self, temp_m3u_file, tmpdir):
        csv_file = tmpdir.join("output.csv")
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.to_file(str(csv_file), format="csv")
        print(csv_file)
        assert os.path.exists(str(csv_file))

    # Test filtering by category
    def test_filter_by_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.remove_by_category('News')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test retrieving by category
    def test_retrieve_by_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.retrieve_by_category('News')
        streams = parser.get_list()
        assert len(streams) == 3

    # Test parsing invalid M3U content
    def test_invalid_m3u_content(self, tmpdir):
        invalid_m3u_file = tmpdir.join("invalid.m3u")
        with open(invalid_m3u_file, "w") as f:
            f.write("Invalid M3U Content")
        parser = M3uParser()
        with pytest.raises(NoStreamsException):
            parser.parse_m3u(str(invalid_m3u_file))
            parser.get_random_stream()
