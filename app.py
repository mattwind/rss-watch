from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import hashlib
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import time
import threading
import schedule

app = Flask(__name__)

urls = [
    "https://wolverine5k.com/sigint.html",
    "https://wolverine5k.com/roe.html",
    "https://wolverine5k.com/hq.html"
]
feed_data = []

def fetch_and_generate_feed():
    global feed_data
    feed_data = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text()
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            domain = urlparse(url).netloc
            feed_data.append({
                "title": domain,
                "link": url,
                "guid": content_hash,
                "description": url
            })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

def generate_rss():
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Website Update"
    ET.SubElement(channel, "link").text = "https://iurkaa3ufa.us-east-1.awsapprunner.com/rss"
    ET.SubElement(channel, "description").text = "Website Update"
    
    for item in feed_data:
        item_element = ET.SubElement(channel, "item")
        ET.SubElement(item_element, "title").text = item["title"]
        ET.SubElement(item_element, "link").text = item["link"]
        ET.SubElement(item_element, "guid").text = item["guid"]
        ET.SubElement(item_element, "description").text = item["description"]
    
    return ET.tostring(rss, encoding="utf-8", method="xml")

@app.route("/rss")
def rss_feed():
    xml_data = generate_rss()
    return Response(xml_data, mimetype="application/rss+xml")

def schedule_task():
    schedule.every(24).hours.do(fetch_and_generate_feed)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    fetch_and_generate_feed()
    threading.Thread(target=schedule_task, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=False)