import re
import os
from urllib.parse import urlparse
from .formatter import Color

def validate_url(url: str) -> bool:
    """Validate if the input is a valid URL."""
    # Add http:// if missing to make urlparse work
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        
    # Check basic URL structure
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def print_banner(formatter):
    """Print the WebDust banner."""
    banner = r"""
 __      __      ___.  ________              .__    
/  \    /  \ ____\_ |__\______ \   __ __ ___|  |_  
\   \/\/   // __ \| __ \|    |  \ |  |  /  ___/  |  
 \        /\  ___/| \_\ \    `   \|  |  \___ \|   __\\
  \__/\  /  \___  >___  /_______  /____//____ >___|
       \/       \/    \/        \/           \/     
                                                 v1.1
    """
    
    formatter._clear_progress()
    print(formatter._colorize(banner, Color.CYAN))
    print(formatter._colorize(" Web Application Reconnaissance Tool", Color.BOLD))
    print(formatter._colorize(" https://github.com/Cr3zy-dev/webdust", Color.BLUE))
    print()
    print(formatter._colorize("=" * 60, Color.CYAN))
    print()
