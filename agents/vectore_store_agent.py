frpm agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
import faiss
import numpy as np
from langchain.embeddings import OpenAIEmbeddings


class VectoreStoreAgent(BaseAgent):
    def __init__(self):
        super().__init__("Vector_store", ZMQ_PUBSUB_PORT,
         ["store_embedding", "search_similar"], AGENT_PORTS["vector_store"])
        self.embeddings = OpenAIEmbeddings()
        self.index = faiss.IndexFlatL2(1536)#openai embedding is 1536 self.embeddings.embedding_dim)
        self.texts = []

    def process_message(self, message):
        if message.action == "store_embedding":
            self.store_embedding(message.data["text"])#, message.data["embedding"])
        elif message.action == "search_similar":
            results = self.search_similar(message.data["query"], message.data["k"])
            self.send_message(message.sender, "similarity_results", {"results": results})

    def store_embedding(self, text):#, embedding):
        embedding = self.embeddings.embed_query(text)
        self.index.add(np.array([embedding]))
        self.texts.append(text)

    def search_similar(self, query, k):
        query_embedding = self.embeddings.embed_query(query)
        D, I = self.index.search(np.array([query_embedding]), k)
        return [self.texts[i] for i in I[0]]