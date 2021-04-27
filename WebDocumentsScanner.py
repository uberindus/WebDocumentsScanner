import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from loguru import logger
from sys import stdout

def is_absolute(url):
	return bool(url.netloc)

def del_query_string(url):
	if not url.netloc:
		return url.path
	else:
		return f"{url.scheme}://{url.netloc}{url.path}"


logger.remove()
logger.add(stdout, colorize=True, format="<blue>INFO:</blue> | <light-yellow>{message}</light-yellow>", level="INFO")

class WebDocumentsScanner:
	"""
    A class used to extracte urls of documents from one or more sites

    ...

	Parameters
    ----------
    root_url : str
        Absolute url which refers to html-document and defines where scanning starts
    limit : int
        Restricts maximum number of visited urls
    allowed_hosts: str
    	Defines for which hosts documents are scanning. Optionally it is set with one element - hostname of 'root_url'
    pos_constraints : set, optional
        Set of regular expressions which defines
         what pattern url must match to be collected
    neg_constraints : int, optional
		Set of regular expressions which defines
         what pattern url must not match to be collected
	ignore_query: bool
		Defines to ignore query string in urls or not. The default is False

    Attributes
    ----------
    visited_urls: set
    	All urls which scanner visited
    internal_links: set
		Set of urls which refer to documents of sites with hostnames from 'allowed_hosts'
    external_links: set
		Set of urls which refer to documents of sites with hostnames not from 'allowed_hosts'
    links: set
    	Union of internal_links and external_links
	"""

	def __init__(self, root_url: str, limit: int, pos_constraints=None, neg_constraints=None,
				 ignore_query=False, allowed_hosts=None):

		if pos_constraints is None:
			pos_constraints = list()
		if neg_constraints is None:
			neg_constraints = list()

		self.root_url = root_url
		self.pos_constraints = pos_constraints
		self.neg_constraints = neg_constraints
		self.limit = limit

		self.internal_links = set()
		self.external_links = set()
		self.links = set()

		self.visited_urls = set()

		self.ignore_query = ignore_query

		if allowed_hosts is None:
			allowed_hosts = set(urlparse(root_url).netloc)

		self.allowed_hosts = allowed_hosts

		self._get_urls()

	def _crawl(self, url):
		current_url = urlparse(url)
		res = requests.get(current_url.geturl())
		if re.search(r"text/html", res.headers.get("Content-Type")):
			soup = BeautifulSoup(res.text, features="html.parser")
			for a in soup.find_all('a'):

				if len(self.visited_urls) == self.limit:
					break

				href = urlparse(a.get('href'))
				if href is None:
					continue

				if is_absolute(href):
					abs_url = href.geturl() if not self.ignore_query else del_query_string(href)

					if href.netloc not in self.allowed_hosts:
						self.visited_urls.add(abs_url)
						if self._meets_constraints(abs_url):
							logger.info(f"External link - {abs_url}")
							self.external_links.add(abs_url)
						continue

				else:
					abs_url = urljoin(current_url.geturl(), href.geturl() if not self.ignore_query else del_query_string(href))

				if abs_url not in self.visited_urls:
					self.visited_urls.add(abs_url)
					if self._meets_constraints(abs_url):
						logger.info(f"Internal link - {abs_url}")
						self.internal_links.add(abs_url)
					self._crawl(abs_url)

	def _meets_constraints(self, url):
		return all(re.match(constraint, url) for constraint in self.pos_constraints) and\
			not any(re.match(constraint, url) for constraint in self.neg_constraints)

	def _get_urls(self):
		self._crawl(self.root_url)
		self.links = self.internal_links | self.external_links