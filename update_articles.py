#!/usr/bin/env python3
"""Get the data from Medium and update articles.yml with the latest articles."""
import re, ssl, html, yaml, logging, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

CONTENT_NS = {"content": "http://purl.org/rss/1.0/modules/content/"}
WORDS_PER_MINUTE = 265  # Medium's own reading speed.
BLURB_MAX_CHARS = 150
USER_AGENT = "Mozilla/5.0 (compatible; about-me-site/1.0; +https://github.com)"

def main():
    """Get the data from Medium and update articles.yml with the latest articles."""
    medium_feed = "https://medium.com/@a.klosowski23"
    logger.info("Starting article update process.")
    articles = get_articles_from_medium(medium_feed)
    update_articles_yml(articles)

def get_articles_from_medium(medium_feed, limit=5):
    """Get the data from Medium: read the RSS feed and return the latest articles."""
    feed_url = build_feed_url(medium_feed)
    logger.info(f"Getting articles from Medium feed {feed_url}")

    request = urllib.request.Request(feed_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30, context=ssl_context()) as response:
        feed = response.read()

    items = ET.fromstring(feed).findall("./channel/item")
    logger.info(f"Found {len(items)} items in the feed.")

    articles = []
    for item in items:
        published = parsedate_to_datetime(item.findtext("pubDate"))
        body = item.findtext("content:encoded", "", CONTENT_NS)
        articles.append({
            "published": published,
            "title": html.unescape((item.findtext("title") or "").strip()),
            "href": clean_href(item.findtext("link") or ""),
            "date": published.strftime("%Y-%m-%d"),
            "read_time": read_time(body),
            "blurb": blurb(body),
        })

    articles.sort(key=lambda article: article["published"], reverse=True)
    latest = [{key: value for key, value in article.items() if key != "published"} for article in articles[:limit]]
    logger.info(f"Keeping the {len(latest)} most recent articles.")
    return latest

def ssl_context():
    """Verify TLS against certifi's CA bundle — python.org builds ship without one of their own."""
    try:
        import certifi
    except ImportError:
        logger.warning("certifi is not installed; falling back to the interpreter's own CA bundle.")
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())

def build_feed_url(medium_feed):
    """Turn a Medium profile URL into its RSS feed URL (a feed URL is left as is)."""
    feed_url = medium_feed.split("?")[0].rstrip("/")
    if not feed_url.endswith("/feed") and "/feed/" not in feed_url:
        feed_url = f"{feed_url}/feed"
    return feed_url

def clean_href(link):
    """Drop Medium's ?source=rss tracking query from an article link."""
    return link.split("?")[0].strip()

def strip_html(markup):
    """Turn a chunk of article HTML into plain text."""
    text = re.sub(r"<[^>]+>", " ", markup)
    text = re.sub(r"\s+", " ", html.unescape(text))
    text = re.sub(r"\s+([,.;:!?)\u2019\u201d])", r"\1", text)  # tags left gaps before punctuation
    return re.sub(r"([(\u201c])\s+", r"\1", text).strip()

def read_time(body):
    """Estimate the reading time of an article from its word count."""
    words = len(strip_html(body).split())
    return f"{max(1, round(words / WORDS_PER_MINUTE))} min"

def blurb(body):
    """Take the opening sentences of the article, up to BLURB_MAX_CHARS."""
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", body, flags=re.DOTALL)
    text = next((stripped for stripped in map(strip_html, paragraphs) if stripped), strip_html(body))
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    opening = sentences[0]
    for sentence in sentences[1:]:
        if len(opening) + len(sentence) + 1 > BLURB_MAX_CHARS:
            break
        opening = f"{opening} {sentence}"

    if len(opening) <= BLURB_MAX_CHARS:
        return opening

    trimmed = opening[:BLURB_MAX_CHARS].rsplit(" ", 1)[0].rstrip(",;:-—– ")
    return f"{trimmed}…"

def update_articles_yml(articles):
    """Update articles.yml with the latest articles."""
    logger.info("Updating articles.yml with the latest articles.")

    with open("articles.yml", "r") as f:
        content = yaml.safe_load(f) or {}

    content.setdefault("medium", {})["articles"] = articles

    with open("articles.yml", "w") as f:
        yaml.dump(content, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
    logger.info("Updated articles.yml successfully.")

if __name__ == "__main__":
    main()
