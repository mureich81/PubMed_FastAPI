from fastapi import FastAPI
import requests

app = FastAPI()
NCBI_API_KEY = "316d1bba625145959e9a88534720c5a4a108"

@app.get("/search_pubmed/")
def search_pubmed(query: str, max_results: int = 10):
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax={max_results}&api_key={NCBI_API_KEY}"
    search_response = requests.get(search_url).json()
    
    pmids = search_response.get("esearchresult", {}).get("idlist", [])
    if not pmids:
        return {"message": "No results found"}

    pmid_str = ",".join(pmids)
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid_str}&retmode=json"
    fetch_response = requests.get(fetch_url).json()

    results = []
    for pmid in pmids:
        article = fetch_response["result"].get(pmid, {})
        results.append({
            "title": article.get("title", "No title"),
            "authors": article.get("authors", []),
            "journal": article.get("source", "Unknown"),
            "pub_date": article.get("pubdate", "Unknown"),
            "pmid": pmid,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })

    return {"articles": results}
