import httpx
import xml.etree.ElementTree as ET

RSS_FEEDS = {
    "techcrunch": "https://feeds.feedburner.com/TechCrunch",
    "wired": "https://www.wired.com/feed/rss",
    "hackernews": "https://hnrss.org/frontpage",
    "google_tech": "https://news.google.com/rss/search?q=technology",
    "ars_technica": "https://feeds.arstechnica.com/arstechnica/index"
}

def fetch_news(source: str = "hackernews", max_results: int = 5):
    url = RSS_FEEDS.get(source, RSS_FEEDS["hackernews"])

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client(timeout=10) as client:  
            response = client.get(url, headers=headers)
            response.raise_for_status()

        root = ET.fromstring(response.content)
        articles = []

        for item in root.findall(".//item")[:max_results]:
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            pub_date = item.find("pubDate")

            if title is not None:
                articles.append({
                    "title": title.text.strip() if title.text else "",
                    "url": link.text.strip() if link is not None and link.text else "",
                    "summary": description.text.strip()[:300] if description is not None and description.text else "",
                    "published": pub_date.text.strip() if pub_date is not None and pub_date.text else ""
                })

        return {"articles": articles, "source": source}

    except Exception as e:
        return {"articles": [], "source": source, "error": str(e)}