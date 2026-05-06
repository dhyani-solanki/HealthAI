import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

load_dotenv()

# ---------- 1. Check API KEY ----------
api_key = os.getenv("GOOGLE_API_KEY")
print("API KEY FOUND:", bool(api_key))


# ---------- 2. Test Gemini ----------
def test_gemini():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0
        )

        response = llm.invoke([HumanMessage(content="Say hello in one sentence.")])
        print("Gemini Response:", response.content)

    except Exception as e:
        print("Gemini Error:", e)


# ---------- 3. Test Embedding ----------
def test_embedding():
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model.encode(["hello world"])
        print("Embedding Working. Vector length:", len(emb[0]))
    except Exception as e:
        print("Embedding Error:", e)


# ---------- 4. Test Scraping ----------
def test_scrape():
    try:
        url = "https://medlineplus.gov/lab-tests/complete-blood-count-cbc/"
        r = requests.get(url, timeout=20)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text()[:300]

        print("Scraping Working. Sample text:")
        print(text)

    except Exception as e:
        print("Scraping Error:", e)


print("\n---- Testing Gemini ----")
test_gemini()

print("\n---- Testing Embeddings ----")
test_embedding()

print("\n---- Testing Scraping ----")
test_scrape()