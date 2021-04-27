# WebDocumentsScanner
A class used to extracte urls of documents from one or more sites
### Usage
##
```python
from WebDocumentsScanner import WebDocumentsScanner
ws = WebDocumentsScanner("https://github.com", 30)

print(*ws.internal_links, sep="\n")
"""
https://github.com/
https://github.com#start-of-content
https://github.com/#start-of-content
https://github.com/join?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home
"""

print(*ws.external_links, sep="\n")
"""
https://docs.github.com/articles/supported-browsers
"""


