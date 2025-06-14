import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

class RAGManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.qa_chain = None
        self.initialize_vector_store()
        
    def initialize_vector_store(self):
        """Initialize or load the vector store."""
        persist_directory = os.path.join("data", "chroma_db")
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        # Initialize QA chain
        template = """You are an expert programmer. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer: Let me help you with that."""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": prompt}
        )
    
    def add_code_to_vector_store(self, code: str, metadata: Dict[str, Any] = None):
        """Add code to the vector store."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text(code)
        
        if metadata is None:
            metadata = {"type": "code"}
            
        self.vector_store.add_texts(
            texts=texts,
            metadatas=[metadata] * len(texts)
        )
        self.vector_store.persist()
    
    def generate_code(self, requirements: str) -> str:
        """Generate code based on requirements using RAG."""
        response = self.qa_chain.run(requirements)
        return response
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for vulnerabilities and improvements."""
        analysis_prompt = f"""Analyze the following code for vulnerabilities and potential improvements.
        Consider:
        1. Security vulnerabilities
        2. Code quality issues
        3. Performance improvements
        4. Best practices
        
        Code to analyze:
        {code}
        
        Provide a detailed analysis."""
        
        analysis = self.qa_chain.run(analysis_prompt)
        return {
            "analysis": analysis,
            "raw_code": code
        }
    
    def search_similar_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code in the vector store."""
        results = self.vector_store.similarity_search_with_score(query, k=n_results)
        return [
            {
                "code": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ] 