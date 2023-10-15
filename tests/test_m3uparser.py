import sys, os, pytest
from pathlib import Path

file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))

from m3u_parser import M3uParser, ParseConfig, SortConfig, FilterConfig


# Sample M3U content for testing
SAMPLE_M3U_CONTENT = """
#EXTM3U
#EXTINF:-1 group-title="News",Channel 1
http://example.com/stream1
#EXTINF:-1 group-title="News",Channel 2
http://example.com/stream2
#EXTINF:-1 group-title="News",Channel 3
http://example.com/stream3
#EXTINF:0,Dlf
#EXTVLCOPT:network-caching=1000
rtsp://10.0.0.1:554/?avm=1&freq=514&bw=8&msys=dvbc&mtype=256qam&sr=6900&specinv=0&pids=0,16,17,18,20,800,810,850
"""


# Fixture to create a temporary M3U file for testing
@pytest.fixture
def temp_m3u_file(tmpdir):
    m3u_file = tmpdir.join("test.m3u")
    with open(m3u_file, "w") as f:
        f.write(SAMPLE_M3U_CONTENT)
    return str(m3u_file)


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
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False, schemes=["rtsp"]))
        streams = parser.get_list()
        assert len(streams) == 4

    # Test filtering by extension
    def test_filter_by_extension(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.retrieve_by_extension('mp4')
        streams = parser.get_list()
        assert len(streams) == 0

    # Test filtering by status
    def test_filter_by_status(self, temp_m3u_file):
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file)
        parser.filter_by('status', 'BAD')
        streams = parser.get_list()
        assert len(streams) == 3

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
        assert os.path.exists(str(json_file))

    # Test saving to CSV file
    def test_save_to_csv(self, temp_m3u_file, tmpdir):
        csv_file = tmpdir.join("output.csv")
        parser = M3uParser()
        parser.parse_m3u(temp_m3u_file, ParseConfig(check_live=False))
        parser.to_file(str(csv_file), format="csv")
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
    # def test_invalid_m3u_content(self, tmpdir):
    #     invalid_m3u_file = tmpdir.join("invalid.m3u")
    #     with open(invalid_m3u_file, "w") as f:
    #         f.write("Invalid M3U Content")
    #     parser = M3uParser()
    #     with pytest.raises(Exception):
    #         parser.parse_m3u(str(invalid_m3u_file))
