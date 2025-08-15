import ChatBot as chatBot
import BrokerBot as brokerBot
import NewsBot as newsBot
import requests
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
import re
import feedparser 
from html import unescape
import os
import csv
from dataclasses import dataclass
import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import time

# Set up rotating log handler
handler = RotatingFileHandler(
    "app.log", maxBytes=5_000_001, backupCount=5  # 5 MB per file, keep 5 backups
)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)

logger = logging.getLogger("my_app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

ticker = ""  
Cik = ""

rss_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={Cik}&count=3&output=atom"


@dataclass
class PotentialBoom:
    ticker: str
    name: str
    event: str
    date_of_catalyst: str

def load_catalysts(filepath: str):
    booms = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            booms.append(PotentialBoom(**row))
    return booms

def parse_sec_submission(file_path):
    WANTED_TYPES = {
        "8-K", "EX-99.1", "EX-99.2", "S-1", "10-K", "10-Q", "DEF 14A", "S-3", "S-4", "424B5", "424B3", "SD", "SC 13G", "SC 13D", "PRE 14A", "DEFA14A", "EX-10.1", "EX-10.2", "EX-23", "EX-21", "EX-31", "EX-32"
    }  # Add/remove as needed for your use case

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    documents = re.findall(r"<DOCUMENT>(.*?)</DOCUMENT>", content, re.DOTALL)
    parsed_docs = []

    for doc in documents:
        doc_type_match = re.search(r"<TYPE>(.*)", doc)
        description_match = re.search(r"<DESCRIPTION>(.*)", doc)
        text_match = re.search(r"<TEXT>(.*)", doc, re.DOTALL)

        doc_type = doc_type_match.group(1).strip() if doc_type_match else ""
        if doc_type not in WANTED_TYPES:
            continue  # Skip unwanted sections

        # Extract and clean the text content
        def remove_tags(text):
            return re.sub(r"<.*?>", "", text, flags=re.DOTALL)

        raw_text = text_match.group(1).strip() if text_match else ""
        raw_text = remove_tags(raw_text)


        patterns = [
            r"(?i)forward[-\s]?looking statements.*?(?=ITEM\s+\d+|SIGNATURES|\Z)",
            r"(?i)safe harbor.*?(?=ITEM\s+\d+|SIGNATURES|\Z)",
            r"(?i)risks related to.*?(?=ITEM\s+\d+|SIGNATURES|\Z)",
            r"(?i)cautionary note.*?(?=ITEM\s+\d+|SIGNATURES|\Z)",
        ]

        for p in patterns:
            raw_text = re.sub(p, "", raw_text, flags=re.DOTALL)

        clean_text = unescape(raw_text)
        # If 8-K, remove everything after "Item 9.01 Financial Statements and Exhibits.\n(d) Exhibits"
       
        clean_text = "\n".join(line.strip() for line in clean_text.splitlines() if line.strip())
        # Remove everything before "standards provided pursuant to Section 13(a) of the Exchange Act."
        marker = "of the Exchange Act."
        idx = clean_text.find(marker)
        if idx != -1:
            clean_text = clean_text[idx:]
        
        if doc_type == "8-K":
            end_marker = "The information contained in this Current Report shall not be deemed"
            end_idx = clean_text.find(end_marker)
            if end_idx != -1:
                clean_text = clean_text[:end_idx]
            end_idx = clean_text.find(end_marker)
            if end_idx != -1:
                clean_text = clean_text[:end_idx + len(end_marker)]
        # Unescape HTML entities and remove excessive blank lines/whitespace
    

        parsed_docs.append({
            "type": doc_type,
            "description": description_match.group(1).strip() if description_match else "",
            "text": clean_text
        })

    return parsed_docs

# Helper function to get CIK for a ticker
def get_cik_for_ticker(ticker):

    dl = Downloader("JustAChillGuy", "JustAChillGuy@gmail.com")
    return dl.ticker_to_cik_mapping[ticker]

# gets  new filings for a given CIK and last known date
def get_new_forms(last_known_date):
    url = f"https://data.sec.gov/submissions/CIK{Cik}.json"
    headers = {"User-Agent": "YourName your@email.com"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    found_dates = []
    found_forms = []
    for form, date in zip(forms[:3], filing_dates[:3]):
        if date > last_known_date:
            found_dates.append(date)
            found_forms.append(form)
    if found_dates:
        return True, found_forms, found_dates
    return False, None, None

def get_last_known_date():
    
    url = f"https://data.sec.gov/submissions/CIK{Cik}.json"
    headers = {"User-Agent": "YourName your@email.com"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    filing_dates = recent.get("filingDate", [])
    return filing_dates[0] if filing_dates else None

def main(forms):

    dl = Downloader("JustAChillGuy", "JustAChillGuy@gmail.com")
    for form in forms:
        dl.get(form, ticker, limit=3, download_details=False)
    
    base_dir = dl.download_folder
    docs = []
    TextWall = ""

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                docs.extend(parse_sec_submission(file_path))

    for doc in docs:
        TextWall += ((f"File Type: {doc['type']}\nQuick Description: {doc['description']}\nText: {doc['text'][:30000]}\n{'-'*40}"))
    
    print(TextWall)

def Initialize():
    brokerBot.Start(False)

def WaitingLoop():
    while True:

        if dt.datetime.now().hour < 9 or dt.datetime.now().hour > 16:
            print("Market is closed. Waiting for next trading day...")
            logger.info("Market is closed. Quitting...")
            exit()
        
        for boom in load_catalysts("Catalysts.csv"):
            if boom.date_of_catalyst == dt.date.today().strftime("%Y-%m-%d"):
                poll_for_catalyst(boom)
                break
        else:
            print("No catalysts for today.")
            #TODO implement a quit here.
            exit()

        
        print("Waiting...")
        brokerBot.ib.sleep(120)

def poll_for_catalyst(boom):
   result =  chatBot.getresponse(f"Find the latest news on {boom.name} they are expecting a positive catalyst: {boom.event} today." +
                                 "Find the expected news. if not found or news found is neutral/unpredictable, then respond with NO ONLY." +  
                                 "else, read the news and guess if the news will make the stock price go up based or down." +
                                 "LOOK FOR THE NEWS, ONLY BUY IF YOU FIND THE ACTUAL POSITIVE CATLYST. if the data/readout/whatever hasn't been released, don't buy."+
                                 "RESPOND WITH UP or DOWN ONLY.")
   if result.lower() == "up":
        print(f"Positive news found for {boom.name} on {boom.event}. Buying stock...")
        
        logger.info(f"Positive news found for {boom.name} on {boom.event}. Buying stock...")

        brokerBot.PlaceBuyBracketOrder(boom.ticker, 1.07, 0.94)
        
   elif result.lower() == "down":
        print(f"No positive news found for {boom.name} on {boom.event}. short selling stock.")

        logger.info(f"No positive news found for {boom.name} on {boom.event}. short selling stock.")

        brokerBot.PlaceShortSellBracketOrder(boom.ticker, 1.07, 0.94)

   elif result.lower() == "no":
        print(f"No news found for {boom.name} on {boom.event}. Not buying stock.")

        logger.info(f"No news found for {boom.name} on {boom.event}. Not buying stock.")

logger.info("Stared")

print("Starting...")
Initialize()


#logger.info("Stared2")
WaitingLoop()