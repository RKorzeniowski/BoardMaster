import requests
import wikipediaapi
from sentence_transformers import SentenceTransformer
import numpy as np
from crewai.tools import BaseTool


SEARCH_TERM = "Monopoly"
LIMIT = 2
TEXT_SIM_ENCODER = SentenceTransformer('all-MiniLM-L6-v2')


def get_most_relevant_index(query, candidates):
    scores = []
    for candidate_text in candidates:
        relevance_score = check_relevance(query, candidate_text)
        scores.append(relevance_score)
    return max(range(len(relevance_score)), key=relevance_score.__getitem__)

def cosine_similarity(x, y):
    x = x.cpu().detach().numpy()
    y = y.cpu().detach().numpy()
    dot_product = np.dot(x, y.T)
    norm_x = np.linalg.norm(x, axis=1, keepdims=True)
    norm_y = np.linalg.norm(y, axis=1, keepdims=True)
    return dot_product / (norm_x * norm_y.T)

def check_relevance(query, candidate_text):
    query_emb = TEXT_SIM_ENCODER.encode([query], convert_to_tensor=True)
    candidate_emb = TEXT_SIM_ENCODER.encode([candidate_text], convert_to_tensor=True)
    score = cosine_similarity(query_emb, candidate_emb)[0][0]
    return score

def get_most_relevant_index(query, candidates):
    scores = [check_relevance(query, text) for text in candidates]
    return int(np.argmax(scores))

def traverse_wiki_page(query, page_or_section):
    # Base case: if this is a leaf node, return its text
    if not page_or_section._section:
        return page_or_section._text

    subsections = page_or_section._section
    candidate_texts = [sub._text for sub in subsections]
    best_index = get_most_relevant_index(query, candidate_texts)
    print("\n Picked subsection: '", subsections[best_index].title, "' out of: ", [x.title for x in subsections])
    print("with text: ", subsections[best_index]._text, "\n")
    return traverse_wiki_page(query, subsections[best_index])


class WikiSearchTool(BaseTool):
    name: str = "Lookup Monopoly Info"
    description: str = "Search Monopoly board, chance/community cards, and basic rules. Input should be a string describing the topic."

    def _run(self, query: str) -> str:
        session = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "opensearch",
            "namespace": "0",
            "search": SEARCH_TERM,
            "limit": LIMIT,
            "format": "json"
        }

        response = session.get(url=URL, params=PARAMS)
        data = response.json()

        wiki_pages = []
        for wiki_title in data[1]:
            wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')
            page_py = wiki_wiki.page(wiki_title)
            wiki_pages.append(page_py)

        page_summaries = [x.summary for x in wiki_pages]

        picked_page_idx = get_most_relevant_index(query, page_summaries)
        picked_page = wiki_pages[picked_page_idx]

        print("When using WikiSearchTool with search term: '", SEARCH_TERM, "' and query: '", query, "' picked page: '", picked_page.title, "' out of: ", [x.title for x in wiki_pages], "\n")

        result_text = traverse_wiki_page(query, picked_page)
        return result_text
