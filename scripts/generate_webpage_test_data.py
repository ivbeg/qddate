#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to generate test data for date detection from webpages.

This script:
1. Fetches HTML content from selected webpages (news sites, blogs)
2. Extracts all text snippets with length < 50 characters
3. Tests each snippet with qddate's match() method
4. Generates a CSV file with columns: text, pattern_key (empty if no match)
"""

import sys
import os
import csv
import re
import argparse
from urllib.parse import urlparse

# Add parent directory to path to import qddate
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests library not available. Install it with: pip install requests")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 library not available. Install it with: pip install beautifulsoup4")

from qddate import DateParser


# Default list of webpages to scrape (government agencies and international organizations)
DEFAULT_URLS = [
    # International Organizations
    'https://www.un.org',
    'https://www.unido.org/news',
    'https://www.worldbank.org',
    'https://www.imf.org',
    'https://www.who.int',
    'https://www.ilo.org',
    'https://www.fao.org',
    'https://www.unesco.org',
    'https://www.oecd.org',
    'https://www.europarl.europa.eu',
    'https://ec.europa.eu',
    'https://www.nato.int',
    'https://www.osce.org',
    'https://www.coe.int',
    'https://www.iaea.org',
    
    # European Government Sites
    'https://www.gov.uk',
    'https://data.gov.uk',
    'https://www.gov.pl',
    'https://data.gouv.fr',
    'https://www.bundesregierung.de',
    'https://www.govdata.de',
    'https://www.governo.it',
    'https://www.dati.gov.it',
    'https://www.government.nl',
    'https://www.belgium.be',
    'https://www.gov.cz',
    'https://www.government.bg',
    'https://www.government.se',
    'https://www.government.no',
    'https://www.valtioneuvosto.fi',
    'https://www.government.ie',
    'https://www.gov.pt',
    'https://www.government.es',
    
    # North American Government Sites
    'https://www.usa.gov',
    'https://www.data.gov',
    'https://www.canada.ca',
    'https://open.canada.ca',
    'https://www.gob.mx',
    
    # Asian Government Sites
    'https://www.gov.sg',
    'https://data.gov.sg',
    'https://www.gov.hk',
    'https://www.gov.in',
    'https://data.gov.in',
    'https://www.gov.au',
    'https://data.gov.au',
    'https://www.gov.nz',
    'https://www.gov.kr',
    'https://www.data.go.kr',
    'https://www.gov.jp',
    
    # Other Government Sites
    'https://www.gov.za',
]


def fetch_url(url, timeout=10):
    """
    Fetch HTML content from a URL.
    
    :param url: URL to fetch
    :type url: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :return: HTML content as string, or None if failed
    :rtype: str|None
    """
    if not REQUESTS_AVAILABLE:
        print(f"Error: requests library required to fetch {url}")
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_text_snippets(html_content, max_length=50):
    """
    Extract text snippets from HTML content.
    
    :param html_content: HTML content as string
    :type html_content: str
    :param max_length: Maximum length of text snippets to extract
    :type max_length: int
    :return: List of text snippets
    :rtype: list[str]
    """
    if not BS4_AVAILABLE:
        # Fallback: simple regex-based extraction
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # Extract text from tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        # Clean up whitespace
        text = ' '.join(text.split())
    else:
        # Use BeautifulSoup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text
        text = soup.get_text(separator=' ', strip=True)
    
    # Split text into snippets of appropriate length
    snippets = set()  # Use set to avoid duplicates
    
    # First, split by common punctuation that might separate date strings
    # This helps isolate potential date strings
    for separator in ['.', ',', ';', ':', '|', '\n', '\t']:
        parts = text.split(separator)
        for part in parts:
            part = part.strip()
            if part and len(part) < max_length and len(part) >= 3:
                snippets.add(part)
    
    # Also extract words and short phrases (2-3 words) for date detection
    words = text.split()
    for i, word in enumerate(words):
        # Clean word
        word = word.strip()
        if word and len(word) < max_length and len(word) >= 3:
            snippets.add(word)
        
        # Try 2-word combinations (common for dates like "Jan 2024")
        if i < len(words) - 1:
            phrase = f"{word} {words[i+1]}".strip()
            if len(phrase) < max_length and len(phrase) >= 3:
                snippets.add(phrase)
        
        # Try 3-word combinations (common for dates like "Jan 15, 2024")
        if i < len(words) - 2:
            phrase = f"{word} {words[i+1]} {words[i+2]}".strip()
            if len(phrase) < max_length and len(phrase) >= 3:
                snippets.add(phrase)
    
    # Filter and clean snippets
    cleaned_snippets = []
    for snippet in snippets:
        # Remove excessive whitespace
        snippet = ' '.join(snippet.split())
        # Skip if too short or empty
        if len(snippet) >= 3 and len(snippet) < max_length:
            cleaned_snippets.append(snippet)
    
    return cleaned_snippets


def process_urls(urls, parser):
    """
    Process URLs and extract date detection results.
    
    :param urls: List of URLs to process
    :type urls: list[str]
    :param parser: qddate DateParser instance
    :type parser: DateParser
    :return: List of tuples (text, pattern_key, url)
    :rtype: list[tuple]
    """
    results = []
    
    for url in urls:
        print(f"Processing {url}...")
        html_content = fetch_url(url)
        if not html_content:
            continue
        
        snippets = extract_text_snippets(html_content, max_length=50)
        print(f"  Extracted {len(snippets)} text snippets")
        
        for snippet in snippets:
            try:
                match_result = parser.match(snippet)
                if match_result:
                    pattern_key = match_result['pattern']['key']
                else:
                    pattern_key = ''
                results.append((snippet, pattern_key, url))
            except Exception as e:
                # If there's an error, still record the snippet with empty pattern
                print(f"  Warning: Error processing snippet '{snippet[:30]}...': {e}")
                results.append((snippet, '', url))
        
        print(f"  Processed {len(snippets)} snippets from {url}")
    
    return results


def write_csv(results, output_file, include_url=True):
    """
    Write results to CSV file.
    
    :param results: List of tuples (text, pattern_key, url)
    :type results: list[tuple]
    :param output_file: Output CSV file path
    :type output_file: str
    :param include_url: Whether to include URL column
    :type include_url: bool
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if include_url:
            fieldnames = ['text', 'pattern_key', 'url']
        else:
            fieldnames = ['text', 'pattern_key']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            if include_url:
                writer.writerow({
                    'text': result[0],
                    'pattern_key': result[1],
                    'url': result[2]
                })
            else:
                writer.writerow({
                    'text': result[0],
                    'pattern_key': result[1]
                })


def main():
    """Main function."""
    parser_arg = argparse.ArgumentParser(
        description='Generate test data for date detection from webpages'
    )
    parser_arg.add_argument(
        '--urls',
        nargs='+',
        help='URLs to process (default: uses built-in list)',
        default=None
    )
    parser_arg.add_argument(
        '--output',
        '-o',
        help='Output CSV file path (default: benchmarks/webpage_test_data.csv)',
        default='benchmarks/webpage_test_data.csv'
    )
    parser_arg.add_argument(
        '--no-url-column',
        action='store_true',
        help='Do not include URL column in CSV'
    )
    parser_arg.add_argument(
        '--max-length',
        type=int,
        default=50,
        help='Maximum length of text snippets to extract (default: 50)'
    )
    
    args = parser_arg.parse_args()
    
    # Check dependencies
    if not REQUESTS_AVAILABLE:
        print("Error: requests library is required. Install it with: pip install requests")
        sys.exit(1)
    
    if not BS4_AVAILABLE:
        print("Warning: beautifulsoup4 is recommended for better HTML parsing.")
        print("Install it with: pip install beautifulsoup4")
    
    # Initialize qddate parser
    print("Initializing qddate parser...")
    qddate_parser = DateParser()
    
    # Get URLs
    urls = args.urls if args.urls else DEFAULT_URLS
    print(f"Processing {len(urls)} URLs...")
    
    # Process URLs
    results = process_urls(urls, qddate_parser)
    
    print(f"\nTotal snippets processed: {len(results)}")
    
    # Count matches
    matches = sum(1 for r in results if r[1])
    print(f"Snippets with date matches: {matches}")
    print(f"Snippets without matches: {len(results) - matches}")
    
    # Write CSV
    output_path = args.output
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\nWriting results to {output_path}...")
    write_csv(results, output_path, include_url=not args.no_url_column)
    print(f"Done! Results written to {output_path}")


if __name__ == '__main__':
    main()

