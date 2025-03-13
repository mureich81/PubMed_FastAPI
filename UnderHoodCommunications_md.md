# PubMed API Integration

## 1. Пользователь отправляет запрос
- Браузер или другой клиент отправляет **GET-запрос** на URL:  
  ```
  http://127.0.0.1:8000/search_pubmed/?query=CRISPR&max_results=5
  ```
- FastAPI принимает этот запрос и передаёт его в функцию `search_pubmed()`.  
- Код, обрабатывающий этот шаг:
  ```python
  @app.get("/search_pubmed/")  
  def search_pubmed(query: str, max_results: int = 10):
  ```

## 2. FastAPI отправляет первый запрос в PubMed API
- Формируется URL для поиска статей по ключевому слову.  
- Отправляется **GET-запрос** к PubMed API:  
  ```python
  search_url = (
      f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
      f"?db=pubmed&term={query}&retmode=json&retmax={max_results}&api_key={NCBI_API_KEY}"
  )
  search_response = requests.get(search_url).json()
  ```
- PubMed возвращает JSON-ответ с **списком PMIDs** (уникальных идентификаторов статей).

## 3. FastAPI получает PMIDs из ответа PubMed
- Код, который извлекает PMIDs из JSON:  
  ```python
  pmids = search_response.get("esearchresult", {}).get("idlist", [])
  if not pmids:
      return {"message": "No results found"}
  ```
- Если статьи не найдены, API возвращает сообщение об отсутствии результатов.  

## 4. FastAPI отправляет второй запрос в PubMed API для получения деталей статей
- Формируется URL с перечислением всех найденных PMIDs.  
- Отправляется **GET-запрос** в PubMed API, чтобы получить метаданные статей:  
  ```python
  pmid_str = ",".join(pmids)  
  fetch_url = (
      f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
      f"?db=pubmed&id={pmid_str}&retmode=json"
  )
  fetch_response = requests.get(fetch_url).json()
  ```

## 5. PubMed возвращает данные о статьях
- JSON-ответ содержит заголовки, авторов, журналы и даты публикации.  
- Код, который обрабатывает ответ и формирует список результатов:  
  ```python
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
  ```

## 6. FastAPI возвращает данные пользователю
- API отправляет **готовый JSON-ответ** обратно клиенту:  
  ```python
  return {"articles": results}
  ```
- Клиент (браузер, Python-скрипт, GPT-S) получает ответ и может его обработать.  

Весь процесс включает два HTTP-запроса к PubMed API и одну отправку ответа пользователю.
