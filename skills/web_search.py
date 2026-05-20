import os
import re
import urllib.parse
import requests
from typing import List, Dict, Any

def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Performs a web search for the given query.
    Supports Tavily API (TAVILY_API_KEY), Serper API (SERPER_API_KEY),
    and falls back to DuckDuckGo HTML parsing or a clean mock fallback.
    
    Args:
        query (str): The search query.
        max_results (int): Maximum number of results to return.
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries with 'title', 'link', and 'snippet'.
    """
    # 1. Try Tavily API if key is present
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "max_results": max_results},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("content", "")
                    })
                if results:
                    return results
        except Exception:
            pass

    # 2. Try Serper API if key is present
    serper_key = os.environ.get("SERPER_API_KEY")
    if serper_key:
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                json={"q": query, "num": max_results},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("organic", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
                if results:
                    return results
        except Exception:
            pass

    # 3. Fallback to DuckDuckGo HTML search
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            # Simple regex parser for DDG HTML results
            # Each result is contained in a class="web-result" block or similar
            results = []
            # We look for result blocks: <a class="result__url" href="..."> or result__snippet
            result_blocks = re.findall(r'<div class="result results_links results_links_deep web-result.*?">.*?</div>\s*</div>\s*</div>', html, re.DOTALL)
            
            if not result_blocks:
                # Secondary simple search in case structure changed slightly
                result_blocks = re.findall(r'<div class="result.*?">.*?</div>\s*</div>', html, re.DOTALL)
                
            for block in result_blocks:
                if len(results) >= max_results:
                    break
                
                # Extract link and title
                link_match = re.search(r'<a class="result__url"[^>]*href="([^"]+)"', block)
                title_match = re.search(r'<a class="result__snippet"[^>]*>([^<]+)</a>', block)
                if not title_match:
                    title_match = re.search(r'<a class="result__link"[^>]*>([^<]+)</a>', block)
                
                # Extract snippet
                snippet_match = re.search(r'<a class="result__snippet"[^>]*>([^<]+)</a>', block)
                if not snippet_match:
                    snippet_match = re.search(r'<div class="result__snippet"[^>]*>([^<]+)</div>', block)
                
                if link_match and title_match:
                    link = link_match.group(1)
                    # Decode DuckDuckGo redirect link if present
                    if "uddg=" in link:
                        link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                    
                    title = title_match.group(1).strip()
                    snippet = snippet_match.group(1).strip() if snippet_match else ""
                    
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
            
            if results:
                return results
    except Exception:
        pass

    # 4. Final elegant mock fallback to ensure the agent never crashes
    return [
        {
            "title": f"Result for '{query}' (Offline/Mock)",
            "link": "https://example.com/search?q=" + urllib.parse.quote(query),
            "snippet": f"This is a high-quality simulated search result for the query: '{query}'. Enable internet connectivity or provide a TAVILY_API_KEY / SERPER_API_KEY environment variable to fetch real-time data."
        }
    ]

if __name__ == "__main__":
    # Quick test
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Artificial Intelligence"
    print(f"Searching for: {q}")
    res = web_search(q, 3)
    for i, r in enumerate(res, 1):
        print(f"\n[{i}] {r['title']}\n    Link: {r['link']}\n    Snippet: {r['snippet']}")
