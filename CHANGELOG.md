# CHANGELOG

## v0.4.2 (2025-10-01)

### Fix

* fix: Resolve issue with file:// URIs ([`3f73cea`](https://github.com/pawanpaudel93/m3u-parser/commit/3f73cea45584ff7d9f32bb15307f95a7dafa271a))

## v0.4.1 (2024-01-30)

### Fix

* fix: Resolve parse_json issue ([`fcc30e2`](https://github.com/pawanpaudel93/m3u-parser/commit/fcc30e22e402266486dfcfd62a15fe795039f565))

### Unknown

* Merge pull request #26 from pawanpaudel93/feat/add-channel-number

feat: Add channel number ([`51f8fa9`](https://github.com/pawanpaudel93/m3u-parser/commit/51f8fa9fb894c751471da9b2ebe51428a9e69e94))

* Merge pull request #25 from www2000/patch-1

Add support for channel number (tvg_chno) ([`57b9957`](https://github.com/pawanpaudel93/m3u-parser/commit/57b9957fc883e5fb02a6ef42a101fe1eac238216))

* Add support for the tvg_chno item to parse_csv and parse_json ([`fb31fa1`](https://github.com/pawanpaudel93/m3u-parser/commit/fb31fa19d4b1e62af31427d227b9101a7bc3e2d7))

* Update m3u_parser.py

add support for channel number tvg_chno that is use in tvheadend ([`8b1d130`](https://github.com/pawanpaudel93/m3u-parser/commit/8b1d1300cf2b0f9d5b3112901a18954b5049a65d))

## v0.4.0 (2023-11-20)

### Chore

* chore: Bump package version #22 #24 ([`1671166`](https://github.com/pawanpaudel93/m3u-parser/commit/16711663ecd3826a6a4af416e145b0021f96ae6e))

* chore: Update README ([`a74d1f2`](https://github.com/pawanpaudel93/m3u-parser/commit/a74d1f29a10bf2bd0528afa1765d572bddb7ebb6))

* chore: Update comments &amp; README ([`652b67d`](https://github.com/pawanpaudel93/m3u-parser/commit/652b67d698103fd6c659379afa97fb3675d0a460))

* chore: Update README.md &amp; code comments ([`e764df0`](https://github.com/pawanpaudel93/m3u-parser/commit/e764df0445f6cfbb3fab2077a21578496261734d))

* chore: isort ([`de4c1c0`](https://github.com/pawanpaudel93/m3u-parser/commit/de4c1c077ab6133b04571aa3b813ff1e453073ba))

* chore: Update README.md ([`7e0ba02`](https://github.com/pawanpaudel93/m3u-parser/commit/7e0ba02dd13e769e0c375a0bbff5f9dea624d778))

* chore: Update README.md ([`8979fe0`](https://github.com/pawanpaudel93/m3u-parser/commit/8979fe0930a026f59839c847312191acfe61658e))

* chore: bump package version ([`279c6c5`](https://github.com/pawanpaudel93/m3u-parser/commit/279c6c572ec736a2dd57d1adb49540880f3d8363))

* chore: Update README.md ([`fa46ad1`](https://github.com/pawanpaudel93/m3u-parser/commit/fa46ad1d783da85e83054bc485666542389d5f83))

* chore: bump package version ([`1e67426`](https://github.com/pawanpaudel93/m3u-parser/commit/1e674264b5cc8cfe63c821e401cfc48bd7538e5c))

* chore: add other implementations to readme ([`e5f7cad`](https://github.com/pawanpaudel93/m3u-parser/commit/e5f7cad6a972a989d28dad107df02b27c919fafe))

* chore: update readme ([`e44202d`](https://github.com/pawanpaudel93/m3u-parser/commit/e44202de8f820c45c6b21469e2b5905357196535))

### Feature

* feat: Add remove duplicates method #24 ([`86c1b30`](https://github.com/pawanpaudel93/m3u-parser/commit/86c1b308b6007e2434755a089739580b288bea49))

* feat: Add live to stream info to match other implementations ([`1c74182`](https://github.com/pawanpaudel93/m3u-parser/commit/1c74182e88b82b0b0ee4a037748ef13cb443429e))

* feat: Add exceptions instead of logging ([`47265ce`](https://github.com/pawanpaudel93/m3u-parser/commit/47265ce68e51e440d1daff16e4c77c4caa4d8782))

* feat: Add schemes support with status checker ([`685a3c9`](https://github.com/pawanpaudel93/m3u-parser/commit/685a3c9e8277b897c4a22d7cdef582bf01fa473a))

* feat: Add methods to parse content from CSV/JSON file/url #18 ([`a468d1e`](https://github.com/pawanpaudel93/m3u-parser/commit/a468d1e06dc52cd1f072b2ef151c41a7451f41c3))

### Fix

* fix: Resolve issue with filter_by handling different filter values ([`ee3ade1`](https://github.com/pawanpaudel93/m3u-parser/commit/ee3ade1900b73010213d46c06bc6674728b23a84))

* fix: Make sure status is either good or bad only ([`305f329`](https://github.com/pawanpaudel93/m3u-parser/commit/305f3293ed00fe01a07b42571ccd9f7c8fcc97e3))

* fix: Update filter_by &amp; sort_by and tests ([`8c45494`](https://github.com/pawanpaudel93/m3u-parser/commit/8c454940a4aee5da5393e98bbbaeb59bcc617b69))

* fix: add type checking and check if url is present ([`43395db`](https://github.com/pawanpaudel93/m3u-parser/commit/43395db6edbcde3fda7e51f95503e84dbc770683))

* fix: setup logger #21 ([`d4393fa`](https://github.com/pawanpaudel93/m3u-parser/commit/d4393fa23b8d5e38d5539c55ea772800d3223e88))

### Refactor

* refactor: Update default schemes ([`aeab036`](https://github.com/pawanpaudel93/m3u-parser/commit/aeab036007143670f997f39aca5e59b8f4fecd4c))

* refactor: Replace requests with urllib ([`4078ed0`](https://github.com/pawanpaudel93/m3u-parser/commit/4078ed013e4a542427e89fcdee7ddf457b8701d1))

* refactor: Remove dataclass ([`10598b2`](https://github.com/pawanpaudel93/m3u-parser/commit/10598b225c28e9e995f2457877fa73475ff0c376))

### Test

* test: Add more tests ([`d8eaa8c`](https://github.com/pawanpaudel93/m3u-parser/commit/d8eaa8cddc2d06f116cf07eb378dbae79a29649c))

* test: Add more tests ([`e84ed29`](https://github.com/pawanpaudel93/m3u-parser/commit/e84ed299a39b6387731815c638d52f14b92b2231))

### Unknown

* Merge pull request #23 from pawanpaudel93/feat/support-schemes

feat: Add schemes support with status checker &amp; support removing duplicates ([`fcd70f3`](https://github.com/pawanpaudel93/m3u-parser/commit/fcd70f300781e06798e335046dba19d3f51b2363))

* Update extension and category function and its comment &amp; readme ([`7595daf`](https://github.com/pawanpaudel93/m3u-parser/commit/7595daf546e2aee50381fc0c1cbfd65c6bcd5b58))

* Updated to 0.2.0 ([`5c62d32`](https://github.com/pawanpaudel93/m3u-parser/commit/5c62d32802d3b1d68c847735444bdee375c055a3))

* Update README.md ([`53b4e5a`](https://github.com/pawanpaudel93/m3u-parser/commit/53b4e5afc51a8447402f033049cfc0d90bacf519))

* set encoding explicitly to utf-8 #14 ([`f8ee743`](https://github.com/pawanpaudel93/m3u-parser/commit/f8ee7431e791d97fce4460ba48d6526deb167b58))

* v0.1.9 ([`b03d24e`](https://github.com/pawanpaudel93/m3u-parser/commit/b03d24ef2d078f730ddee68729bd86e8c12b6eb2))

* Fix file reading error caused by unquote #15 ([`f2b844b`](https://github.com/pawanpaudel93/m3u-parser/commit/f2b844bb48e569291899380a154dde9a26c6c669))

## v0.1.8 (2021-12-29)

### Unknown

* v0.1.8 ([`133d536`](https://github.com/pawanpaudel93/m3u-parser/commit/133d536e28dd28a3f18cde54f39c5f6335e4e9b3))

* modified url checker + added regex for acestream #16 ([`cfb07f0`](https://github.com/pawanpaudel93/m3u-parser/commit/cfb07f0353d828380d44ee8869eed295b28b64db))

* setup black with isort ([`000bde1`](https://github.com/pawanpaudel93/m3u-parser/commit/000bde13656264ca93b445e4f3529ec7c376e5a7))

* Merge pull request #13 from dineiar/master

Renaming trim to enforce_schema in parse_m3u ([`babc496`](https://github.com/pawanpaudel93/m3u-parser/commit/babc496a77f29103a2536fde2a5fa1df40057ef0))

* Fix to avoid outputting &#34;None&#34; in M3U (#13) ([`319a918`](https://github.com/pawanpaudel93/m3u-parser/commit/319a918bc79ef2d47a0d07ec913ffaa28d3c37c6))

* Fixed mistake pointed in #13 ([`f34cd0d`](https://github.com/pawanpaudel93/m3u-parser/commit/f34cd0d7221260bbbda52b655b531de95eddcbab))

* Including empty keys and removed exception masking ([`33ddd09`](https://github.com/pawanpaudel93/m3u-parser/commit/33ddd099effa945b7332069e9cc26c883093d0f4))

* Renaming trim to enforce_schema ([`e831ea4`](https://github.com/pawanpaudel93/m3u-parser/commit/e831ea42411e01ea9b1fe036c5853c8938a88ea0))

* UPDATED README ([`be151e9`](https://github.com/pawanpaudel93/m3u-parser/commit/be151e95d71a26aeea3f32755194c1e687cb2e78))

* fetching title containing comma #12 ([`eadadf6`](https://github.com/pawanpaudel93/m3u-parser/commit/eadadf69bc8521b2cf31c9b4ea7b8bc47edd3320))

* Added trim parameter for parsing and code cleanup #11 ([`4a414ad`](https://github.com/pawanpaudel93/m3u-parser/commit/4a414ad9cd143d4703d5e71c1d4d7d5a1885fdb7))

* Fixed m3u generation with optional keys (320f7598) ([`eaa2d87`](https://github.com/pawanpaudel93/m3u-parser/commit/eaa2d87a8f41766a080c7a674657d9de3d4fb589))

* Reuses compiled regex and fixes #10 ([`320f759`](https://github.com/pawanpaudel93/m3u-parser/commit/320f7598fb6450253b12d9ace362672557c2687b))

* added support for saving to m3u format #7 ([`5e284b1`](https://github.com/pawanpaudel93/m3u-parser/commit/5e284b18f0087f854a62522f239e1646d81fb972))

* updated readme ([`b6ec317`](https://github.com/pawanpaudel93/m3u-parser/commit/b6ec317e19ad0c6fd084f4a1d0a2bdf885572605))

* removing language &amp; country if not present and minor modification #10 ([`7d42d1d`](https://github.com/pawanpaudel93/m3u-parser/commit/7d42d1d23eebaf2aefea34e3ed424f5c99210f4c))

* Merge pull request #9 from dineiar/master

Fixes removal of streams with multiple filters #8 ([`fc70a89`](https://github.com/pawanpaudel93/m3u-parser/commit/fc70a897b7c2baded79f1a687c0fd73ac6644168))

* Fixes #8 ([`d59e593`](https://github.com/pawanpaudel93/m3u-parser/commit/d59e59357bc5d12bf248f2ac25d86fcd1780ec29))

* fixing minor errors and adding filepath regex #6 ([`36273e0`](https://github.com/pawanpaudel93/m3u-parser/commit/36273e0c3cdfd3fc595361947509c98e234920b7))

* updated readme ([`1e820d8`](https://github.com/pawanpaudel93/m3u-parser/commit/1e820d8e3e4269a417259f6f2a4b9b90b30f88f6))

* url replaced with correct path variable #2 ([`be5fd17`](https://github.com/pawanpaudel93/m3u-parser/commit/be5fd174bb955434499ff4eb4330a222c5631984))

* edited readme ([`1ba439b`](https://github.com/pawanpaudel93/m3u-parser/commit/1ba439b903e1428c759a4814eebb15ed1989fc7e))

* added license ([`1cee93b`](https://github.com/pawanpaudel93/m3u-parser/commit/1cee93b9c8d019378c72afd91953c008da60d041))

* added README ([`71f45ad`](https://github.com/pawanpaudel93/m3u-parser/commit/71f45ad7e2be5ca34b7cffd1baafce2f920ee0ef))

* handeled key error exception and formatted the code ([`93e5418`](https://github.com/pawanpaudel93/m3u-parser/commit/93e54186934cd2a2a19ba862952a1021b5e4c4cf))

* django facing RuntimeError solved ([`04410d2`](https://github.com/pawanpaudel93/m3u-parser/commit/04410d21fe8ecd683d3b8b91e556596d6b769ad5))

* solving module not found error ([`623c62b`](https://github.com/pawanpaudel93/m3u-parser/commit/623c62beabe689b0b340e688349067750eedbd49))

* updated gitignore and dependencies and minor changes on m3u parser ([`d59b92d`](https://github.com/pawanpaudel93/m3u-parser/commit/d59b92dfc68d092521c75e3069f54e3b2b9ae02f))

* added docs string ([`daa84ba`](https://github.com/pawanpaudel93/m3u-parser/commit/daa84bab599d4fb038aec741c6b9e4fd6f5705dd))

* fixed nested key issues and added live links checking ([`46bcec2`](https://github.com/pawanpaudel93/m3u-parser/commit/46bcec2ea8b32912ff9fe126650e7e6ad2a86b8c))

* added to fetch m3u links from first and second line ([`2a3d48d`](https://github.com/pawanpaudel93/m3u-parser/commit/2a3d48d2009bed540fa7d332af5dbe4b6f7265ed))

* nested dict to csv added and changed json output format ([`fbeabc7`](https://github.com/pawanpaudel93/m3u-parser/commit/fbeabc7cf155d59618d0c64f6c5cf73f5a00641a))

* parse from file, filtering, sorting added ([`884d503`](https://github.com/pawanpaudel93/m3u-parser/commit/884d50363eef77bf7d42c6df50e86d39ff504178))

* parse from url added ([`6984d09`](https://github.com/pawanpaudel93/m3u-parser/commit/6984d09fa852be95e607b773d4c49fe5d2116c75))
