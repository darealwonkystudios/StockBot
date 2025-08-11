
import datetime as dt

TogetherAPIKey = "9b063679d208383fe3590644d40cc4ba90ddf213af5772395d80d570087ba84a"
NewsAPIKey = "6a8bb318a95b4a6784f3bedf6ca5e370"
newsurl = "https://newsapi.org/v2/top-headlines"
tavily_api_key="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"
import os
import requests
from bs4 import BeautifulSoup
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
import together
import requests
from bs4 import BeautifulSoup
from readability.readability import Document
import textwrap
class TogetherLLM(LLM):
    model: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
    temperature: float = 0.3
    max_tokens: int = 5000
    together_api_key: Optional[str] = TogetherAPIKey

    @property
    def _llm_type(self) -> str:
        return "together-custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        together.api_key = self.together_api_key
        response = together.Complete.create(
            prompt=prompt,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stop=stop,
            together_api_key= TogetherAPIKey
        )
        return response["choices"][0]["text"]
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
# ChatBot.py


class EnhancedWebScraperTool:
    def __init__(self):
        self.name = "WebScraper"
        self.description = "Scrape content from a website with advanced options. Input should be a URL"

    def run(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Use readability to extract main content
            doc = Document(response.text)
            title = doc.short_title()
            soup = BeautifulSoup(doc.summary(), "html.parser")

            # Remove unwanted tags
            for tag in soup(["script", "style", "footer", "nav", "aside"]):
                tag.extract()

            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            max_length = 4000
            if len(clean_text) > max_length:
                clean_text = textwrap.shorten(clean_text, width=max_length, placeholder="...\n[Content truncated due to length]")

            return f"Title: {title}\nURL: {url}\n\n{clean_text}"

        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
            
# Initialize Together AI LLM
llm = TogetherLLM()

# Web search tool (Tavily)

search = GoogleSearchAPIWrapper(google_cse_id="96d018ec0a566479c", google_api_key="AIzaSyAzEyCWEUsY4_sICH3d7_X5D0UJVWIrS_Q")

tools = [
    Tool(
        name="Web Search",
        func=search.run,
        description="Useful for answering questions about current events from the internet."
    ),

    Tool(
        name="Web Scraper",
        func=search.run,
        description="Useful for scraping text from a specific website. Use to get richer context. Input should be a URL."
    )
]

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    webscraper = EnhancedWebScraperTool(),
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def getresponse(prompt):
    response = agent.run(prompt)
    return response
# Run the agent
while False:
    query = input("You: ")
    if query.lower() in ["exit", "quit"]:
        break
    result = agent.run(query)
    print("\n🤖 Agent:", result)
