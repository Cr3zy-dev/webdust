from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Set
import os

class Analyzer:
    """Analyzes discovered URLs for potential vulnerabilities."""
    
    def __init__(self, formatter, wordlist_config=None):
        self.formatter = formatter
        self.wordlist_config = wordlist_config or {}
        
        # Define default parameter patterns for classification
        self.default_idor_patterns = {'id', 'user_id', 'account_id', 'uuid', 'guid', 'userid'}
        self.default_lfi_patterns = {'file', 'path', 'lang', 'page', 'include', 'dir', 'folder', 'template'}
        self.default_redirect_patterns = {'url', 'redirect', 'next', 'redir', 'return', 'to', 'goto', 'link'}
        self.default_xss_patterns = {'q', 'query', 'search', 'keyword', 'name', 'message', 'input', 'content'}
        self.default_sqli_patterns = {'category', 'sort', 'order', 'filter', 'where', 'select'}
        
        # Load and merge custom wordlists with defaults
        self.idor_patterns = self._load_patterns('idor', self.default_idor_patterns)
        self.lfi_patterns = self._load_patterns('lfi', self.default_lfi_patterns)
        self.redirect_patterns = self._load_patterns('redir', self.default_redirect_patterns)
        self.xss_patterns = self._load_patterns('xss', self.default_xss_patterns)
        self.sqli_patterns = self._load_patterns('sqli', self.default_sqli_patterns)
        
    def _load_patterns(self, category: str, default_patterns: Set[str]) -> Set[str]:
        """Load patterns from wordlist file and merge with defaults."""
        patterns = default_patterns.copy()
        
        if category not in self.wordlist_config:
            return patterns
            
        wordlist_path = self.wordlist_config[category]
        
        if not os.path.isfile(wordlist_path):
            self.formatter.print_warning(f"Custom {category.upper()} wordlist not found: {wordlist_path}")
            return patterns
            
        try:
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                custom_patterns = set()
                for line in f:
                    line = line.strip().lower()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        custom_patterns.add(line)
                        
                if custom_patterns:
                    patterns.update(custom_patterns)
                    self.formatter.print_success(f"Loaded {len(custom_patterns)} custom {category.upper()} patterns")
                else:
                    self.formatter.print_warning(f"No valid patterns found in {category.upper()} wordlist")
                    
        except Exception as e:
            self.formatter.print_error(f"Failed to load {category.upper()} wordlist: {str(e)}")
            
        return patterns
        
    def analyze_urls(self, discovered_urls: List[Dict]) -> List[Dict]:
        """Analyze all discovered URLs for potential vulnerabilities."""
        self.formatter.print_status(f"Analyzing {len(discovered_urls)} discovered URLs...")
        
        # Print pattern statistics
        total_default = (len(self.default_idor_patterns) + len(self.default_lfi_patterns) + 
                        len(self.default_redirect_patterns) + len(self.default_xss_patterns) + 
                        len(self.default_sqli_patterns))
        total_current = (len(self.idor_patterns) + len(self.lfi_patterns) + 
                        len(self.redirect_patterns) + len(self.xss_patterns) + 
                        len(self.sqli_patterns))
        
        if total_current > total_default:
            custom_count = total_current - total_default
            self.formatter.print_info(f"Using {total_current} patterns ({total_default} default + {custom_count} custom)")
        else:
            self.formatter.print_info(f"Using {total_current} default patterns")
        
        results = []
        
        for url_info in discovered_urls:
            url = url_info['url']
            params = url_info['params']
            
            # Skip JavaScript files for parameter analysis
            if url_info.get('js_file'):
                url_info['vectors'] = ['JS']
                results.append(url_info)
                continue
                
            # Identify potential vectors
            vectors = self._identify_vectors(url, params, url_info)
            
            # Add vectors to URL info
            url_info['vectors'] = vectors
            results.append(url_info)
            
        return results
    
    def _identify_vectors(self, url: str, params: Dict, url_info: Dict) -> List[str]:
        """Identify potential vulnerability vectors based on URL and parameters."""
        vectors = []
        
        # Check for parameter-based vulnerabilities
        if params:
            # Convert parameters to lowercase for matching
            param_names = {k.lower() for k in params.keys()}
            
            # Check for IDOR patterns
            if any(pattern in param_names for pattern in self.idor_patterns):
                vectors.append('IDOR')
                
            # Check for LFI patterns
            if any(pattern in param_names for pattern in self.lfi_patterns):
                vectors.append('LFI')
                
            # Check for Open Redirect patterns
            if any(pattern in param_names for pattern in self.redirect_patterns):
                vectors.append('REDIR')
                
            # Check for XSS patterns
            if any(pattern in param_names for pattern in self.xss_patterns):
                vectors.append('XSS')
                
            # Check for SQLi patterns
            if any(pattern in param_names for pattern in self.sqli_patterns):
                vectors.append('SQLI')
        
        # Check for form-based vulnerabilities
        if url_info.get('has_form'):
            vectors.append('FORM')
            
        # Check for file upload vulnerabilities
        if url_info.get('has_upload'):
            vectors.append('UPLOAD')
            
        # If no specific vectors found but has parameters, mark as potential XSS
        if params and not vectors:
            vectors.append('XSS')
            
        # If still no vectors but has a form, mark as potential CSRF
        if not vectors and url_info.get('has_form'):
            vectors.append('CSRF')
            
        # Add additional classifications based on URL path
        path = urlparse(url).path.lower()
        
        if 'admin' in path or 'dashboard' in path:
            vectors.append('ADMIN')
            
        if 'api' in path or 'rest' in path or 'graphql' in path:
            vectors.append('API')
            
        if 'login' in path or 'auth' in path or 'signin' in path:
            vectors.append('AUTH')
            
        # If no vectors identified, mark as INFO
        if not vectors:
            vectors.append('INFO')
            
        return vectors
