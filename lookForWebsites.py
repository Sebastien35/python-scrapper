import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


def extract_phone_numbers(html):
    phone_patterns = [
        r"\b\d{10}\b",  # 10-digit number
        r"\+\d{11}",  # International format
        r"\(\d{3}\)\s?\d{3}-?\d{4}",  # US format
        r"\d{3}\s\d{3}\s\d{4}",  # European format
        r"\b0\d{1,2} \d{2,4} \d{2,4} \d{2,4}\b",  # French format with spaces
    ]

    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, html))

    return list(set(phone_numbers))  # Remove duplicates


def search_web(keywords, limit=100):
    search_url = f"https://html.duckduckgo.com/html/?q={'+'.join(keywords.split())}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        links = set()

        # Find all search result links
        for link in soup.find_all("a", class_="result__url"):
            full_url = link.get("href")
            if full_url:
                links.add(full_url)
            if len(links) >= limit:  # Limit to the specified number
                break

        return links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the search results: {e}")
        return set()


def get_links(url, visited):
    try:
        html = get_html(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            links = set()

            # Find all anchor tags with href attributes
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                full_url = urljoin(url, href)  # Join base URL with the href
                if urlparse(full_url).netloc == urlparse(url).netloc:  # Same domain
                    links.add(full_url)

            return links
        else:
            return set()
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return set()


def main(input_keywords, output_file):
    try:
        # Perform search and get URLs
        urls = search_web(input_keywords, limit=100)

        visited_urls = set()  # Keep track of visited URLs
        all_phone_numbers = {}  # Store phone numbers by URL

        for url in urls:
            url = url.strip()  # Remove any leading/trailing whitespace
            if url:  # Check if the URL is not empty
                print(f"Processing {url}...")

                # Collect phone numbers from the URL
                html = get_html(url)
                if html:
                    phone_numbers = extract_phone_numbers(html)
                    all_phone_numbers[url] = phone_numbers

        # Write results to output file
        with open(output_file, "w") as outfile:
            for url, phone_numbers in all_phone_numbers.items():
                outfile.write(f"Phone Numbers found in {url}:\n")
                if phone_numbers:
                    for number in phone_numbers:
                        outfile.write(f"{number}\n")  # Write the full match directly
                else:
                    outfile.write("No phone numbers found.\n")
                outfile.write("\n")  # Add a newline for better readability

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    input_keywords = input("Enter keywords to search for: ")
    main(input_keywords, "output.txt")
