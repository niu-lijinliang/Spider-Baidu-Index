# Spider
Crawl Baidu Index including KEYWORD, SOURCE, DATE, AREA, INDEX.

This program is easy. It just simulate your own account to crawl the Baidu Index.

# Usage

## Requirement
python3.5+

requests

## Set config.py
### Cookie
Use Chrome to get cookie while logged in.
- Open the Baidu Index using Chrome while logged in
- Press F12 to enter the console and select network
- Refresh the page, and you'll see some things.
Select the index.html, you can get the cookie from the right window.
- Copy the Cookie to `COOKIE`

### Other Settings
The comment of config.py provides the code for all areas. Choose some for `AREA_CODE` 

You can provide any number of `KEYWORDS`, but this will only crawl 5 keywords at a time.

`DATE` needs to be no earlier than 2011-1-1

`KIND` corresponds to 3 data sources on Baidu 
Index
