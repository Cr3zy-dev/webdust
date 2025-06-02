from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Set

class Analyzer:
    """Analyzes discovered URLs for potential vulnerabilities."""
    
    def __init__(self, formatter):
        self.formatter = formatter
        
        # Define parameter patterns for classification
        self.idor_patterns = {'id', 'user_id', 'account_id', 'uuid', 'guid', 'userid'}
        self.lfi_patterns = {'file', 'path', 'lang', 'page', 'include', 'dir', 'folder', 'template'}
        self.redirect_patterns = {'url', 'redirect', 'next', 'redir', 'return', 'to', 'goto', 'link'}
        self.xss_patterns = {'q', 'query', 'search', 'keyword', 'name', 'message', 'input', 'content'}
        self.sqli_patterns = {'category', 'sort', 'order', 'filter', 'where', 'select'}
        
    def analyze_urls(self, discovered_urls: List[Dict]) -> List[Dict]:
        """Analyze all discovered URLs for potential vulnerabilities."""
        self.formatter.print_status(f"Analyzing {len(discovered_urls)} discovered URLs...")
        
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