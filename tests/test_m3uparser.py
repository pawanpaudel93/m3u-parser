import sys, os
from pathlib import Path

file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))

from m3u_parser import M3uParser, ParseConfig

m3u_file_content = '''#EXTM3U
#EXTINF:0,Dlf
#EXTVLCOPT:network-caching=1000
rtsp://10.0.0.1:554/?avm=1&freq=514&bw=8&msys=dvbc&mtype=256qam&sr=6900&specinv=0&pids=0,16,17,18,20,800,810,850'''

test_file_path = "test.m3u"


def test_parse():
    async def get_status(url):
        return "GOOD"

    with open(test_file_path, "w") as f:
        f.write(m3u_file_content)

    parser = M3uParser(timeout=5)
    parser.parse_m3u(test_file_path, ParseConfig(schemes=["rtsp"], status_checker={"rtsp": get_status}))
    parser.remove_by_extension("mp4")
    parser.filter_by("status", "GOOD")
    parser.to_file(test_file_path.replace(".m3u", ".json"))

    assert len(parser.get_list()) == 1

    # Remove temporary files
    os.remove(test_file_path.replace(".m3u", ".json"))
    os.remove(test_file_path)
