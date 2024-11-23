from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
from crawl4ai import Crawler
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("documentation", ZMQ_PUBSUB_PORT, ["scrape_docs"], AGENT_PORTS["documentation"])
        self.crawler = Crawler()
        self.llm = OpenAI(temperature=0.7)

    def process_message(self, message):
        if message.action == "scrape_docs":
            docs = self.scrape_documentation()
            processed_docs = self.process_documentation(docs)
            self.send_message("analysis", "update_knowledge", {"docs": processed_docs})

    def scrape_documentation(self):
        url = "https://owasp.org/www-project-juice-shop/"
        content = self.crawler.crawl(url)
        # Extract relevant sections using BeautifulSoup
        # This is a simplified example; you'd need to implement more sophisticated extraction
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        docs = soup.find_all('section', class_='content')
        return [doc.text for doc in docs]

    def process_documentation(self, docs):
        template = """
        Summarize the following documentation about web application security:
        {doc}
        
        Provide a concise summary focusing on:
        1. Key vulnerabilities
        2. Best practices for prevention
        3. Detection techniques
        """
        prompt = PromptTemplate(template=template, input_variables=["doc"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        
        processed_docs = []
        for doc in docs:
            summary = llm_chain.run(doc)
            processed_docs.append(summary)
        
        return processed_docs