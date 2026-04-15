"""
Web Scraper Module for The International Renju Federation (RenjuNet)
"""
import requests
from bs4 import BeautifulSoup
import json
import logging
import time

# Initialize logging for auditing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_renjunet_strategies(urls: list[str], output_filename: str = "renjunet_knowledge.json") -> None:
    """
    Scrapes educational and strategic content from RenjuNet URLs and processes it into chunked JSON.

    Args:
        urls (list[str]): A list of RenjuNet article URLs to scrape.
        output_filename (str): The destination JSON file for the structured data.
    """
    knowledge_base = []
    chunk_id = 1

    for url in urls:
        logger.info(f"Fetching data from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text from paragraphs (adjust selectors based on specific RenjuNet page structures)
            paragraphs = soup.find_all('p')
            
            for p in paragraphs:
                text_content = p.get_text(strip=True)
                # Filter out extremely short UI text or empty lines to ensure high data density
                if len(text_content) > 50:
                    knowledge_base.append({
                        "id": f"kb-renju-{chunk_id}",
                        "text": f"Source: RenjuNet. Strategy Concept: {text_content}"
                    })
                    chunk_id += 1
            
            # Polite delay to respect the target server
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")

    # Save to JSON
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=4, ensure_ascii=False)
    
    logger.info(f"✅ Successfully scraped and saved {len(knowledge_base)} knowledge chunks to {output_filename}.")

if __name__ == "__main__":
    # Example Target URLs (You can expand this list with specific tutorial pages)
    TARGET_URLS = [
        "http://www.renju.net/study/rules.php",
        # Add more specific strategy URLs here
    ]
    scrape_renjunet_strategies(TARGET_URLS)