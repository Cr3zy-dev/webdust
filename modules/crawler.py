import time
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import List, Dict, Set

class Crawler:
    """WebDust crawler to discover URLs, forms, and upload fields."""
    
    def __init__(self, formatter, verbose=False):
        self.formatter = formatter
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WebDust/1.1 (+https://github.com/Cr3zy-dev/webdust)'
        })
        self.visited: Set[str] = set()
        self.discovered_urls: List[Dict] = []
        self.total_urls = 0
        self.current_url = 0
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{('?' + parsed.query) if parsed.query else ''}"
    
    def crawl(self, base_url: str, max_depth: int) -> List[Dict]:
        """Crawl the website starting from base_url up to max_depth."""
        self.formatter.print_status(f"Starting crawl from {base_url} with depth {max_depth}")
        
        # Start with the base URL at depth 0
        urls_to_visit = [(base_url, 0)]
        
        while urls_to_visit:
            url, depth = urls_to_visit.pop(0)
            
            # Normalize URL
            url = self.normalize_url(url)
            
            # Skip if already visited
            if url in self.visited:
                continue
                
            # Mark as visited
            self.visited.add(url)
            
            # Increment progress counter
            self.current_url += 1
            
            # Display progress
            self.formatter.print_progress(f"Crawling ({self.current_url}/{self.total_urls or '?'}): {url}")
            
            try:
                # Fetch the page
                response = self.session.get(url, timeout=10)
                
                # Skip non-HTML responses
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    if 'javascript' in content_type.lower():
                        self.discovered_urls.append({
                            'url': url,
                            'params': {},
                            'has_form': False,
                            'has_upload': False,
                            'js_file': True,
                            'status_code': response.status_code
                        })
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page details
                url_info = self._extract_page_info(url, soup, response)
                self.discovered_urls.append(url_info)
                
                # Stop if we've reached max depth
                if depth >= max_depth:
                    continue
                
                # Find all links on the page
                new_urls = self._extract_links(base_url, url, soup)
                
                # Update total URL count estimation
                self.total_urls = max(self.total_urls, self.current_url + len(new_urls))
                
                # Add new URLs to the queue
                for new_url in new_urls:
                    if new_url not in self.visited:
                        urls_to_visit.append((new_url, depth + 1))
                        
            except requests.RequestException as e:
                if self.verbose:
                    self.formatter.print_warning(f"Error fetching {url}: {str(e)}")
                continue
            
            # Small delay to be nice to the server
            time.sleep(0.1)
            
        self.formatter._clear_progress()
        self.formatter.print_success(f"Crawl complete. Discovered {len(self.discovered_urls)} unique endpoints.")
        return self.discovered_urls
    
    def _extract_links(self, base_url: str, current_url: str, soup: BeautifulSoup) -> List[str]:
        """Extract all links from the page."""
        links = []
        
        # Get all <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links, javascript: links, and anchors
            if not href or href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                continue
                
            # Resolve relative URLs
            absolute_url = urljoin(current_url, href)
            
            # Only follow links within the same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
                
        return links
    
    def _extract_page_info(self, url: str, soup: BeautifulSoup, response) -> Dict:
        """Extract forms, parameters, and other details from the page."""
        parsed_url = urlparse(url)
        
        # Check for query parameters
        params = parse_qs(parsed_url.query)
        
        # Check for forms
        forms = soup.find_all('form')
        has_form = len(forms) > 0
        
        # Check for file upload fields
        file_inputs = soup.find_all('input', {'type': 'file'})
        has_upload = len(file_inputs) > 0
        
        # Find JavaScript files
        js_links = [script['src'] for script in soup.find_all('script', src=True)]
        
        # Add discovered JS files to the crawl list
        for js_link in js_links:
            js_url = urljoin(url, js_link)
            if urlparse(js_url).netloc == urlparse(url).netloc and js_url not in self.visited:
                self.visited.add(js_url)
                self.discovered_urls.append({
                    'url': js_url,
                    'params': {},
                    'has_form': False,
                    'has_upload': False,
                    'js_file': True,
                    'status_code': 0  # We haven't fetched it yet
                })
        
        return {
            'url': url,
            'params': params,
            'has_form': has_form,
            'has_upload': has_upload,
            'js_file': False,
            'status_code': response.status_code
        }
