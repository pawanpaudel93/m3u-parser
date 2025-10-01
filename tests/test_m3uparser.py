import json
import os
import sys
from pathlib import Path

import pytest

file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))

from m3u_parser import M3uParser
from m3u_parser.exceptions import KeyNotFoundException, NoStreamsException, ParamNotPassedException

# Sample M3U content for testing
SAMPLE_M3U_CONTENT = """
#EXTM3U
#EXTINF:-1 tvg-id="Channel 1" tvg-chno="1" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="NP" tvg-language="Newari" group-title="News",Channel 1
http://example.com/stream1
#EXTINF:-1 tvg-id="Channel 2" tvg-chno="2" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="IN" tvg-language="Hindi" group-title="News",Channel 2
http://example.com/stream2
#EXTINF:-1 tvg-id="Channel 3" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="CN" tvg-language="Chinesee" group-title="News",Channel 3
http://example.com/stream3
#EXTINF:0,Dlf
#EXTVLCOPT:network-caching=1000
rtsp://10.0.0.1:554/?avm=1&freq=514&bw=8&msys=dvbc&mtype=256qam&sr=6900&specinv=0&pids=0,16,17,18,20,800,810,850
"""

DUPLICATE_M3U_CONTENT = """
#EXTM3U
#EXTINF:-1 tvg-id="Channel 1" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="NP" tvg-language="Newari" group-title="News",Channel 1
http://example.com/stream1
#EXTINF:-1 tvg-id="Channel 1" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="NP" tvg-language="Newari" group-title="News",Channel 1
http://example.com/stream1
#EXTINF:-1 tvg-id="Channel 2" tvg-logo="https://i.imgur.com/AvCQYgu.png" tvg-country="CN" tvg-language="Chinesee" group-title="News",Channel 2
http://example.com/stream2
"""

SAMPLE_JSON_CONTENT = json.dumps(
    [
        {
            "name": "Channel 1",
            "logo": "https://i.imgur.com/AvCQYgu.png",
            "url": "http://example.com/stream1",
            "category": "News",
            "tvg": {"id": "Channel 1", "name": None, "url": None, "chno": "1"},
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

SAMPLE_CSV_CONTENT = """name,logo,url,category,tvg_id,tvg_name,tvg_url,tvg_chno,country_code,country_name,language_code,language_name
Channel 1,https://i.imgur.com/AvCQYgu.png,http://example.com/stream1,News,Channel 1,,,1,NP,Nepal,new,Newari
Channel 2,https://i.imgur.com/AvCQYgu.png,http://example.com/stream2,News,Channel 2,,,2,IN,India,hin,Hindi
Channel 3,https://i.imgur.com/AvCQYgu.png,http://example.com/stream3,News,Channel 3,,,3,CN,China,,Chinesee
"""


MIXED_SCHEMES_M3U_CONTENT = """#EXTM3U
#EXTINF:-1,A1 TV Rajasthan (576p)
https://yuppftalive.akamaized.net/080823/a1tv/playlist.m3u8
#EXTINF:235,Henrik José - They Killed the Kid
file:///Users/user/Music/Bliss%20-%20They%20Killed%20the%20Kid.mp3
#EXTINF:447,Ultrasyd - Campylobacter's Groove
file:///Users/user/Music/Ultrasyd%20-%20Campylobacter%27s%20Groove.mp3
#EXTINF:-1 tvg-id="Channel 1" tvg-logo="https://i.imgur.com/AvCQYgu.png" group-title="News",Channel 1
http://example.com/stream1
"""


async def rtsp_checker(url: str):
    return True


# Fixture to create a temporary M3U file for testing
@pytest.fixture
def temp_m3u_file(tmpdir):
    m3u_file = tmpdir.join("test.m3u")
    with open(m3u_file, "w") as f:
        f.write(SAMPLE_M3U_CONTENT)
    return str(m3u_file)


@pytest.fixture
def temp_duplicate_m3u_file(tmpdir):
    m3u_file = tmpdir.join("test.m3u")
    with open(m3u_file, "w") as f:
        f.write(DUPLICATE_M3U_CONTENT)
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


# Fixture to create a temporary M3U file with mixed schemes for testing
@pytest.fixture
def temp_mixed_schemes_m3u(tmpdir):
    m3u_file = tmpdir.join("test_mixed_schemes.m3u")
    with open(m3u_file, "w") as f:
        f.write(MIXED_SCHEMES_M3U_CONTENT)
    return str(m3u_file)


# Test M3uParser class
class TestM3uParser:
    # Test parsing of M3U content
    def test_parse_m3u(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        streams = parser.get_list()
        assert len(streams) == 3

    # Test parsing of M3U content
    def test_parse_m3u_with_schemes(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(
            temp_m3u_file,
            check_live=True,
            schemes=["http", "https", "rtsp"],
            status_checker={"rtsp": rtsp_checker},
        )
        streams = parser.get_list()
        assert len(streams) == 4

    def test_parse_json(self, temp_json_file):
        parser = M3uParser()
        parser.parse_json(temp_json_file, check_live=False)
        streams = parser.get_list()
        assert len(streams) == 3

    def test_parse_csv(self, temp_csv_file):
        parser = M3uParser()
        parser.parse_csv(temp_csv_file, check_live=False)
        streams = parser.get_list()
        assert len(streams) == 3

    # Test filtering by extension
    def test_filter_by_extension(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.retrieve_by_extension('mp4')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test filtering by nested key
    def test_filter_by_nested_key(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file)
        parser.filter_by('language.code', None, key_splitter=".", retrieve=False, nested_key=True)
        streams = parser.get_list()
        assert len(streams) == 2

    # Test filtering by invalid category
    def test_filter_by_invalid_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.filter_by('category', 'Invalid')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test filtering by invalid category
    def test_filter_by_invalid_key(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        with pytest.raises(KeyNotFoundException):
            parser.filter_by('invalid', 'Invalid')

    # Test filtering by live
    def test_filter_by_live(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=True, schemes=["http", "https", "rtsp"])
        parser.filter_by("live", False)
        streams = parser.get_list()
        assert len(streams) == 4

    # Test filtering by live when check_live is False
    def test_filter_by_live_when_check_live_false(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False, schemes=["http", "https", "rtsp"])
        with pytest.raises(KeyNotFoundException):
            parser.filter_by("live", False)

    # Test sorting by stream name in ascending order
    def test_sort_by_name_asc(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.sort_by('name')
        streams = parser.get_list()
        assert streams[0]['name'] == 'Channel 1'
        assert streams[1]['name'] == 'Channel 2'
        assert streams[2]['name'] == 'Channel 3'

    # Test sorting by stream name in descending order
    def test_sort_by_name_desc(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.sort_by('name', asc=False)
        streams = parser.get_list()
        assert streams[0]['name'] == 'Channel 3'
        assert streams[1]['name'] == 'Channel 2'
        assert streams[2]['name'] == 'Channel 1'

    # Test resetting operations
    def test_reset_operations(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.retrieve_by_extension('mp4')
        parser.reset_operations()
        streams = parser.get_list()
        assert len(streams) == 3

    # Test saving to JSON file
    def test_save_to_json(self, temp_m3u_file, tmpdir):
        json_file = tmpdir.join("output.json")
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.to_file(str(json_file), format="json")
        print(json_file)
        assert os.path.exists(str(json_file))
        os.remove(str(json_file))

    # Test saving to CSV file
    def test_save_to_csv(self, temp_m3u_file, tmpdir):
        csv_file = tmpdir.join("output.csv")
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.to_file(str(csv_file), format="csv")
        print(csv_file)
        assert os.path.exists(str(csv_file))
        os.remove(str(csv_file))

    # Test filtering by category
    def test_filter_by_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
        parser.remove_by_category('News')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test retrieving by category
    def test_retrieve_by_category(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, check_live=False)
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

    def test_remove_specific_duplicates(self, temp_duplicate_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_duplicate_m3u_file, check_live=False)
        parser.remove_duplicates("Channel 1", "http://example.com/stream1")
        streams = parser.get_list()
        assert len(streams) == 2

    def test_remove_all_duplicates(self, temp_duplicate_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_duplicate_m3u_file, check_live=False)
        parser.remove_duplicates()
        streams = parser.get_list()
        assert len(streams) == 2

    def test_remove_duplicates_name_param_only(self, temp_duplicate_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_duplicate_m3u_file, check_live=False)
        with pytest.raises(ParamNotPassedException):
            parser.remove_duplicates("Channel 1")

    def test_remove_duplicates_url_param_only(self, temp_duplicate_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_duplicate_m3u_file, check_live=False)
        with pytest.raises(ParamNotPassedException):
            parser.remove_duplicates(url="http://example.com/stream1")

    # Test parsing M3U with mixed http/https and file:// URIs
    def test_parse_m3u_with_mixed_schemes(self, temp_mixed_schemes_m3u):
        parser = M3uParser()
        parser.parse_m3u(temp_mixed_schemes_m3u, check_live=False, schemes=["http", "https", "file"])
        streams = parser.get_list()
        assert len(streams) == 4
        # Check that all schemes are parsed correctly
        urls = [stream['url'] for stream in streams]
        assert any(url.startswith('https://') for url in urls)
        assert any(url.startswith('http://') for url in urls)
        assert any(url.startswith('file:///') for url in urls)

    # Test mixed schemes with filtering
    def test_filter_mixed_schemes(self, temp_mixed_schemes_m3u):
        parser = M3uParser()
        parser.parse_m3u(temp_mixed_schemes_m3u, check_live=False, schemes=["http", "https", "file"])
        # Filter to only get file:// URIs
        parser.filter_by('url', r'^file:///', retrieve=True)
        streams = parser.get_list()
        assert len(streams) == 2
        assert all(stream['url'].startswith('file:///') for stream in streams)
