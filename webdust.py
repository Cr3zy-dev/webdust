#!/usr/bin/env python3

import argparse
import sys
import time
from urllib.parse import urlparse

from modules.crawler import Crawler
from modules.analyzer import Analyzer
from modules.formatter import Formatter, Color
from modules.utils import validate_url, print_banner


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WebDust - Web Application Reconnaissance Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("-u", "--url", required=True,
                        help="Target URL to scan (e.g., https://example.com)")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="Crawl depth (default: 2)")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable colored output")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("-o", "--output", help="Save results to file")
    
    return parser.parse_args()


def main():
    """Main function to run WebDust."""
    args = parse_arguments()
    
    # Initialize formatter with color setting
    formatter = Formatter(use_color=not args.no_color)
    
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
    
    # Start timer
    start_time = time.time()
    
    try:
        # Initialize crawler
        crawler = Crawler(formatter=formatter, verbose=args.verbose)
        analyzer = Analyzer(formatter=formatter)
        
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