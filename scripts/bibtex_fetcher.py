"""Fetch authentic BibTeX from Crossref and arXiv APIs."""
import requests
import sys
import re
import xml.etree.ElementTree as ET


def crossref_search(fuzzy_title):
    """Step 1: Try Crossref first."""
    search_url = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": fuzzy_title,
        "rows": 3,
        "mailto": "claude_code_user@example.com"
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("message", {}).get("items", [])
        if not items:
            return None

        query_lower = fuzzy_title.lower()
        for item in items:
            title = item.get("title", [""])[0]
            title_lower = title.lower()
            query_words = set(re.findall(r'\w+', query_lower))
            title_words = set(re.findall(r'\w+', title_lower))
            if not query_words or not title_words:
                continue
            overlap = len(query_words & title_words) / max(len(query_words), len(title_words))
            if overlap >= 0.6:
                doi = item.get("DOI")
                bibtex_url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
                headers = {
                    "Accept": "application/x-bibtex",
                    "mailto": "claude_code_user@example.com"
                }
                bibtex_response = requests.get(bibtex_url, headers=headers, timeout=10)
                bibtex_response.raise_for_status()
                bibtex_response.encoding = 'utf-8'
                print(f"[Crossref] {title} (DOI: {doi})\n")
                print(bibtex_response.text)
                return True

        return None
    except Exception as e:
        print(f"Crossref error: {e}", file=sys.stderr)
        return None


def arxiv_search(fuzzy_title):
    """Step 2: Fallback to arXiv API."""
    search_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f'ti:"{fuzzy_title}"',
        "max_results": 1,
        "sortBy": "relevance"
    }

    try:
        response = requests.get(search_url, params=params, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)

        if not entries:
            return None

        entry = entries[0]
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        title = re.sub(r'\s+', ' ', title)

        arxiv_id_raw = entry.find('atom:id', ns).text.strip()
        arxiv_id = arxiv_id_raw.split('/abs/')[-1]
        arxiv_id = re.sub(r'v\d+$', '', arxiv_id)

        authors = []
        for author_elem in entry.findall('atom:author', ns):
            name = author_elem.find('atom:name', ns).text.strip()
            authors.append(name)

        published = entry.find('atom:published', ns).text.strip()
        year = published[:4]

        first_author_last = authors[0].split()[-1].lower() if authors else "unknown"
        first_word = re.findall(r'\w+', title.lower())[0] if title else "paper"
        cite_key = f"{first_author_last}{year}{first_word}"

        author_str = " and ".join(authors)

        bibtex = (
            f"@article{{{cite_key}},\n"
            f"  title={{{title}}},\n"
            f"  author={{{author_str}}},\n"
            f"  journal={{arXiv preprint arXiv:{arxiv_id}}},\n"
            f"  year={{{year}}}\n"
            f"}}"
        )

        print(f"[arXiv] {title} (arXiv: {arxiv_id})\n")
        print(bibtex)
        return True

    except Exception as e:
        print(f"arXiv error: {e}", file=sys.stderr)
        return None


def get_real_bibtex(fuzzy_title):
    result = crossref_search(fuzzy_title)

    if result is None:
        result = arxiv_search(fuzzy_title)

    if result is None:
        print("Not found. Please provide a more accurate title.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        get_real_bibtex(query)
    else:
        print("Please provide a paper title as argument.")
