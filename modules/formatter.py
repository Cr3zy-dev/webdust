import os
import sys
import time
from enum import Enum
from typing import List, Dict, Optional


class Color(Enum):
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class Formatter:
    """Handles the formatting and display of WebDust output."""
    
    def __init__(self, use_color=True):
        """Initialize the formatter with color settings."""
        self.use_color = use_color and self._supports_color()
        self.last_progress_length = 0
        
    def _supports_color(self) -> bool:
        """Check if the terminal supports color output."""
        # Check if running in a terminal
        if not sys.stdout.isatty():
            return False
            
        # Check for NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False
            
        # Check for Windows (cmd/powershell)
        if os.name == 'nt':
            return os.environ.get('ANSICON') is not None or \
                   'WT_SESSION' in os.environ or \
                   'TERM_PROGRAM' in os.environ
                   
        # For Unix-like systems, check TERM
        term = os.environ.get('TERM', '')
        return term != 'dumb'
        
    def _colorize(self, text: str, color: Color) -> str:
        """Apply color to text if color is enabled."""
        if not self.use_color:
            return text
        return f"{color.value}{text}{Color.RESET.value}"
        
    def print_info(self, message: str) -> None:
        """Print informational message."""
        prefix = self._colorize('[i]', Color.BLUE)
        print(f"{prefix} {message}")
        
    def print_status(self, message: str) -> None:
        """Print status message."""
        prefix = self._colorize('[+]', Color.GREEN)
        print(f"{prefix} {message}")
        
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        prefix = self._colorize('[!]', Color.YELLOW)
        print(f"{prefix} {message}")
        
    def print_error(self, message: str) -> None:
        """Print error message."""
        prefix = self._colorize('[x]', Color.RED)
        print(f"{prefix} {message}")
        
    def print_success(self, message: str) -> None:
        """Print success message."""
        prefix = self._colorize('[✓]', Color.CYAN)
        print(f"{prefix} {message}")
        
    def print_progress(self, message: str) -> None:
        """Print progress message with overwrite."""
        # Clear previous line if needed
        if self.last_progress_length > 0:
            print('\r' + ' ' * self.last_progress_length, end='\r')
            
        # Print new progress
        prefix = self._colorize('[+]', Color.GREEN)
        progress_message = f"{prefix} {message}"
        print(progress_message, end='\r')
        
        # Store length for next overwrite
        self.last_progress_length = len(progress_message)
        sys.stdout.flush()
        
    def _clear_progress(self) -> None:
        """Clear the progress line."""
        if self.last_progress_length > 0:
            print('\r' + ' ' * self.last_progress_length, end='\r')
            self.last_progress_length = 0
            sys.stdout.flush()
        
    def print_header(self, message: str) -> None:
        """Print a header with box styling."""
        self._clear_progress()
        width = len(message) + 4
        
        if self.use_color:
            box_top = self._colorize('┌' + '─' * (width - 2) + '┐', Color.CYAN)
            box_bottom = self._colorize('└' + '─' * (width - 2) + '┘', Color.CYAN)
            box_middle = self._colorize('│', Color.CYAN) + ' ' + self._colorize(message, Color.BOLD) + ' ' + self._colorize('│', Color.CYAN)
        else:
            box_top = '┌' + '─' * (width - 2) + '┐'
            box_bottom = '└' + '─' * (width - 2) + '┘'
            box_middle = '│ ' + message + ' │'
            
        print(box_top)
        print(box_middle)
        print(box_bottom)
        
    def print_results(self, results: List[Dict], elapsed_time: float, domain: str) -> None:
        """Print the analysis results in a formatted table."""
        self._clear_progress()
        
        # Count the number of vectors found
        vector_count = sum(len(r.get('vectors', [])) for r in results)
        
        # Print header with summary
        self.print_header(f"WebDust Results for {domain}")
        self.print_success(f"Analysis complete ({len(results)} endpoints, {vector_count} vectors)")
        self.print_info(f"Time elapsed: {elapsed_time:.2f} seconds")
        print()
        
        # Get terminal width
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 120  # fallback width
            
        # Define column widths based on terminal size
        url_width = terminal_width - 35  # Reserve space for other columns
        col_widths = {
            'url': url_width,
            'params': 6,
            'form': 4,
            'upload': 6,
            'vectors': 15
        }
        
        # Print table header
        headers = ['URL', 'PARAMS', 'FORM', 'UPLOAD', 'VECTORS']
        header_row = ' '.join(h.ljust(col_widths[k.lower()]) for h, k in zip(headers, ['url', 'params', 'form', 'upload', 'vectors']))
        
        print(self._colorize(header_row, Color.BOLD))
        print(self._colorize('─' * terminal_width, Color.BLUE))
        
        # Print table rows
        for result in results:
            url = result['url']
            params_count = len(result['params'])
            has_form = 'Yes' if result.get('has_form') else 'No'
            has_upload = 'Yes' if result.get('has_upload') else 'No'
            vectors = ', '.join(result.get('vectors', ['INFO']))
            
            # Format URL to fit in column while preserving important parts
            if len(url) > col_widths['url']:
                # Split URL into parts
                scheme_netloc = url.split('//')[-1].split('/')[0]
                path_parts = url[len(scheme_netloc) + 8:].split('?')
                path = path_parts[0]
                query = f"?{path_parts[1]}" if len(path_parts) > 1 else ""
                
                # Calculate available space
                available_space = col_widths['url'] - len(scheme_netloc) - 5  # 5 for "://" and "..."
                
                if len(path) > available_space:
                    # Truncate the middle of the path
                    half_space = (available_space - 3) // 2
                    path = path[:half_space] + "..." + path[-half_space:]
                
                url = f"{scheme_netloc}/{path}{query}"
                
            # Format row
            url_col = url.ljust(col_widths['url'])
            params_col = str(params_count).ljust(col_widths['params'])
            form_col = has_form.ljust(col_widths['form'])
            upload_col = has_upload.ljust(col_widths['upload'])
            vectors_col = vectors.ljust(col_widths['vectors'])
            
            # Apply color to vectors based on severity
            if any(v in ['IDOR', 'LFI', 'SQLI', 'RCE'] for v in result.get('vectors', [])):
                vectors_col = self._colorize(vectors_col, Color.RED)
            elif any(v in ['XSS', 'CSRF', 'UPLOAD', 'REDIR'] for v in result.get('vectors', [])):
                vectors_col = self._colorize(vectors_col, Color.YELLOW)
            elif any(v in ['FORM', 'AUTH', 'ADMIN'] for v in result.get('vectors', [])):
                vectors_col = self._colorize(vectors_col, Color.MAGENTA)
            
            # Apply color to URL based on status code
            status_code = result.get('status_code', 0)
            if status_code >= 400:
                url_col = self._colorize(url_col, Color.RED)
            elif status_code >= 300:
                url_col = self._colorize(url_col, Color.YELLOW)
            elif status_code >= 200:
                url_col = self._colorize(url_col, Color.GREEN)
                
            # Highlight forms and uploads
            if has_form == 'Yes':
                form_col = self._colorize(form_col, Color.MAGENTA)
            if has_upload == 'Yes':
                upload_col = self._colorize(upload_col, Color.RED)
                
            # Format parameters count
            if params_count > 0:
                params_col = self._colorize(params_col, Color.CYAN)
                
            row = f"{url_col} {params_col} {form_col} {upload_col} {vectors_col}"
            print(row)
            
        print()
        
    def save_results(self, results: List[Dict], filename: str, domain: str, elapsed_time: float) -> None:
        """Save results to a file."""
        with open(filename, 'w') as f:
            f.write(f"WebDust Results for {domain}\n")
            f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {elapsed_time:.2f} seconds\n")
            f.write(f"Endpoints: {len(results)}\n\n")
            
            # Write table header
            f.write(f"{'URL':<50} {'PARAMS':<10} {'FORM':<6} {'UPLOAD':<8} {'VECTORS':<20}\n")
            f.write('-' * 100 + '\n')
            
            # Write table rows
            for result in results:
                url = result['url']
                params_count = len(result['params'])
                has_form = 'Yes' if result.get('has_form') else 'No'
                has_upload = 'Yes' if result.get('has_upload') else 'No'
                vectors = ', '.join(result.get('vectors', ['INFO']))
                
                f.write(f"{url[:50]:<50} {params_count:<10} {has_form:<6} {has_upload:<8} {vectors:<20}\n")