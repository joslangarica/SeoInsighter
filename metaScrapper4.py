import requests
import json
import ssl
import socket
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
from textstat import flesch_reading_ease
import xml.etree.ElementTree as ET
import nltk
import re
import whois
from datetime import datetime

nltk.download('punkt')
nltk.download('stopwords')


def filter_spanish_stopwords(words):
    spanish_stopwords = set(stopwords.words('spanish'))
    custom_stopwords = {'y', 'que', 'la', 'en', 'el', 'un', 'una'}

    all_stopwords = spanish_stopwords.union(custom_stopwords)
    filtered_words = [word for word in words if word.lower() not in all_stopwords]

    return filtered_words


def get_domain_age(domain):
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            age = (datetime.now() - creation_date).days
            return age
    except Exception as e:
        return None


def get_canonical_url(soup):
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        return canonical_link.get('href')
    return None


def get_robots_txt(url):
    robots_url = urljoin(url, 'robots.txt')
    response = requests.get(robots_url)

    if response.status_code == 200:
        return response.text
    else:
        return None


def extract_seo_data(url):
    response = requests.get(url)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')

    # Meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_description.get('content', '') if meta_description else None

    # Meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    meta_keywords = meta_keywords.get('content', '') if meta_keywords else None

    # Title tag
    title_tag = soup.title.string if soup.title else None

    # Canonical URL
    canonical_url = get_canonical_url(soup)

    # Domain age
    domain = urlparse(url).hostname
    domain_age = get_domain_age(domain)

    # Robots.txt
    robots_txt = get_robots_txt(url)

    # Word count and keyword density
    text_content = ' '.join(soup.stripped_strings)
    tokens = word_tokenize(text_content)
    words = [word.lower() for word in tokens if word.isalpha()]
    filtered_words = filter_spanish_stopwords(words)  # Filter out Spanish stopwords
    word_count = len(filtered_words)
    freq_dist = FreqDist(filtered_words)
    keyword_density = {word: count / word_count for word, count in freq_dist.items()}

    # Headers
    headers = {}
    for i in range(1, 7):
        headers[f'H{i}'] = [header.get_text(strip=True) for header in soup.find_all(f'h{i}')]

    # Alt attributes
    alt_attributes = [img.get('alt', '') for img in soup.find_all('img')]

    # Image sources
    images_src = [img.get('src', '') for img in soup.find_all('img')]

    # Links
    links = [link.get('href') for link in soup.find_all('a')]

    # Readability score
    readability = flesch_reading_ease(text_content)

    # Number of images
    image_count = len(soup.find_all('img'))

    # Number of links
    link_count = len(links)

    seo_data = {
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
        'title_tag': title_tag,
        'canonical_url': canonical_url,
        'domain_age': domain_age,
        'robots_txt': robots_txt,
        'word_count': word_count,
        'keyword_density': keyword_density,
        'headers': headers,
        'alt_attributes': alt_attributes,
        'images_src': images_src,
        'links': links,
        'readability_score': readability,
        'number_of_images': image_count,
        'number_of_links': link_count,
    }

    return seo_data


def check_xml_sitemap(url):
    sitemap_url = urljoin(url, 'sitemap.xml')
    response = requests.get(sitemap_url)

    if response.status_code == 200:
        try:
            tree = ET.fromstring(response.content)
            return True
        except ET.ParseError:
            return False
    else:
        return False


def check_ssl_certificate(url):
    domain = urlparse(url).hostname
    context = ssl.create_default_context()

    try:
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                certificate = ssock.getpeercert()
        return True
    except Exception as e:
        return False


def main():
    url = 'https://palosanto.ai'
    seo_data = extract_seo_data(url)

    if seo_data is None:
        print("Failed to extract SEO data. Exiting.")
        return

    seo_data['xml_sitemap_exists'] = check_xml_sitemap(url)
    seo_data['ssl_certificate_valid'] = check_ssl_certificate(url)

    with open('seo_data.json', 'w') as outfile:
        json.dump(seo_data, outfile, indent=4)


if __name__ == "__main__":
    main()