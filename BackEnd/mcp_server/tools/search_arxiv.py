import httpx
import xml.etree.ElementTree as ET

ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

def search_arxiv(topic: str, max_results: int = 5):
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }

    with httpx.Client(timeout=10) as client:  
        response = client.get(ARXIV_BASE_URL, params=params)
        response.raise_for_status()

    root = ET.fromstring(response.content)
    papers = []

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        papers.append({
            "title": entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            "abstract": entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
            "url": entry.find('{http://www.w3.org/2005/Atom}id').text
        })

    return {"papers": papers}