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
    # Updated regular expression pattern for phone numbers
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


def main(input_file, output_file):
    try:
        with open(input_file, "r") as file:
            urls = file.readlines()

        visited_urls = set()  # Keep track of visited URLs
        all_phone_numbers = {}  # Store phone numbers by URL

        for url in urls:
            url = url.strip()  # Remove any leading/trailing whitespace
            if url:  # Check if the URL is not empty
                print(f"Processing {url}...")

                # Get all sub-URLs from the main URL
                sub_urls = get_links(url, visited_urls)
                visited_urls.add(url)  # Mark the main URL as visited

                # Collect phone numbers from the main URL
                html = get_html(url)
                if html:
                    phone_numbers = extract_phone_numbers(html)
                    all_phone_numbers[url] = phone_numbers

                # Collect phone numbers from each sub-URL
                for sub_url in sub_urls:
                    if sub_url not in visited_urls:
                        print(f"Processing sub-URL: {sub_url}...")
                        visited_urls.add(sub_url)  # Mark sub-URL as visited
                        html = get_html(sub_url)
                        if html:
                            phone_numbers = extract_phone_numbers(html)
                            all_phone_numbers[sub_url] = phone_numbers

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

    except FileNotFoundError:
        print("The input file does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main("input.txt", "output.txt")
