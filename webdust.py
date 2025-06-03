#!/usr/bin/env python3

import argparse
import sys
import time
import json
import os
from urllib.parse import urlparse

from modules.crawler import Crawler
from modules.analyzer import Analyzer
from modules.formatter import Formatter, Color
from modules.utils import validate_url, print_banner


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WebDust - Web Application Reconnaissance Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("-u", "--url", required=True,
                        help="Target URL to scan (e.g., https://example.com)")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="Crawl depth (default: 2)")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable colored output (default: False)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output (default: False)")
    parser.add_argument("-o", "--output", 
                        help="Save results to file (default: None)")
    parser.add_argument("-w", "--wordlist", action="store_true",
                        help="Configure custom wordlists for vulnerability detection (default: False)")
    parser.add_argument("-s", "--show", action="store_true",
                        help="Show currently configured custom wordlists")
    
    return parser.parse_args()


def get_wordlist_config_path():
    """Get the path to the wordlist configuration file."""
    # Create webdust directory if it doesn't exist
    config_dir = os.path.join(".", "webdust")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "webdust_wordlists.json")


def configure_wordlists(formatter):
    """Interactive configuration of custom wordlists."""
    config_path = get_wordlist_config_path()
    
    formatter.print_status("Configuring custom wordlists...")
    formatter.print_info("Enter file paths for each vulnerability category (press Enter to skip):")
    print()
    
    categories = {
        'sqli': 'SQL Injection',
        'xss': 'Cross-Site Scripting (XSS)',
        'lfi': 'Local File Inclusion (LFI)',
        'idor': 'Insecure Direct Object References (IDOR)',
        'redir': 'Open Redirect'
    }
    
    config = {}
    
    for category, description in categories.items():
        while True:
            path = input(f"{description} wordlist path: ").strip()
            
            if not path:
                formatter.print_info(f"Skipping {description} wordlist")
                break
                
            if os.path.isfile(path):
                config[category] = path
                formatter.print_success(f"Added {description} wordlist: {path}")
                break
            else:
                formatter.print_error(f"File not found: {path}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    break
    
    # Save configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        formatter.print_success(f"Configuration saved to {config_path}")
        
        if config:
            formatter.print_info(f"Configured {len(config)} custom wordlists")
        else:
            formatter.print_warning("No custom wordlists configured")
            
    except Exception as e:
        formatter.print_error(f"Failed to save configuration: {str(e)}")


def show_wordlist_config(formatter):
    """Display current wordlist configuration."""
    config_path = get_wordlist_config_path()
    
    if not os.path.isfile(config_path):
        formatter.print_info("No custom wordlists configured.")
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        if not config:
            formatter.print_info("No custom wordlists configured.")
            return
            
        formatter.print_header("Custom Wordlist Configuration")
        
        categories = {
            'sqli': 'SQL Injection',
            'xss': 'Cross-Site Scripting (XSS)',
            'lfi': 'Local File Inclusion (LFI)',
            'idor': 'Insecure Direct Object References (IDOR)',
            'redir': 'Open Redirect'
        }
        
        for category, description in categories.items():
            if category in config:
                path = config[category]
                status = "✓" if os.path.isfile(path) else "✗ (file not found)"
                formatter.print_info(f"{description}: {path} {status}")
            else:
                formatter.print_info(f"{description}: Not configured")
                
    except Exception as e:
        formatter.print_error(f"Failed to read configuration: {str(e)}")


def load_wordlist_config():
    """Load wordlist configuration from JSON file."""
    config_path = get_wordlist_config_path()
    
    if not os.path.isfile(config_path):
        return {}
        
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    """Main function to run WebDust."""
    args = parse_arguments()
    
    # Initialize formatter with color setting
    formatter = Formatter(use_color=not args.no_color)
    
    # Handle wordlist configuration mode
    if args.wordlist:
        print_banner(formatter)
        configure_wordlists(formatter)
        return
    
    # Handle show wordlists mode
    if args.show:
        print_banner(formatter)
        show_wordlist_config(formatter)
        return
    
    # Require URL for scanning
    if not args.url:
        formatter.print_error("URL is required for scanning. Use -u/--url or see --help")
        sys.exit(1)
    
    # Print banner
    print_banner(formatter)
    
    # Validate URL
    if not validate_url(args.url):
        formatter.print_error(f"Invalid URL: {args.url}")
        sys.exit(1)
    
    # Add http:// if missing
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
        formatter.print_info(f"URL updated to: {args.url}")
    
    # Parse domain for display
    domain = urlparse(args.url).netloc
    formatter.print_status(f"Target: {domain}")
    formatter.print_status(f"Crawl depth: {args.depth}")
    
    # Load custom wordlist configuration
    wordlist_config = load_wordlist_config()
    if wordlist_config:
        formatter.print_info(f"Loaded {len(wordlist_config)} custom wordlist(s)")
    
    # Start timer
    start_time = time.time()
    
    try:
        # Initialize crawler and analyzer with wordlist config
        crawler = Crawler(formatter=formatter, verbose=args.verbose)
        analyzer = Analyzer(formatter=formatter, wordlist_config=wordlist_config)
        
        # Start crawling
        formatter.print_status("Starting crawl...")
        discovered_urls = crawler.crawl(args.url, args.depth)
        
        if not discovered_urls:
            formatter.print_warning("No URLs discovered during crawl!")
            sys.exit(0)
            
        # Analyze discovered URLs
        formatter.print_status("Analyzing discovered endpoints...")
        results = analyzer.analyze_urls(discovered_urls)
        
        # Display results
        elapsed_time = time.time() - start_time
        formatter.print_results(results, elapsed_time, domain)
        
        # Save to file if specified
        if args.output:
            formatter.save_results(results, args.output, domain, elapsed_time)
            formatter.print_success(f"Results saved to {args.output}")
        
    except KeyboardInterrupt:
        formatter.print_error("\nScan interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"An error occurred: {str(e)}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
