import nltk
from newspaper import Article


def generate_summary(url: str) -> str:
    article = Article(url)
    article.download()
    article.parse()

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab")
    finally:
        article.nlp()

    return article.summary
