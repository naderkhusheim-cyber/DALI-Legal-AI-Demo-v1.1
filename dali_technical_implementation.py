#!/usr/bin/env python3
"""
DALI Legal AI MVP - Technical Implementation
Development of Ambitious Leading Ideas @ Siyada Tech

A lightweight legal AI system using Ollama, Firecrawl, and Chroma
"""

import os
import json
import requests
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import streamlit as st
from datetime import datetime

class DALILegalAI:
    """
    DALI Legal AI MVP Implementation
    
    A lightweight legal AI system that combines:
    - Ollama for local LLM inference
    - Firecrawl for intelligent web scraping
    - Chroma for vector storage and retrieval
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./dali_vectordb"
        ))
        self.collection = self.chroma_client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "DALI Legal Document Collection"}
        )
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except:
            return []
    
    def scrape_with_firecrawl(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website using Firecrawl API
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        if not self.firecrawl_api_key:
            return {"error": "Firecrawl API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "formats": ["markdown", "html"],
            "onlyMainContent": True,
            "includeTags": ["title", "meta", "h1", "h2", "h3", "p", "article"],
            "excludeTags": ["nav", "footer", "aside", "script", "style"]
        }
        
        try:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Firecrawl API error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Ollama
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        payload = {
            "model": "nomic-embed-text",
            "prompt": text
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get("embedding", [])
            return []
        except:
            return []
    
    def add_document_to_vectordb(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Add a document to the vector database
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Success status
        """
        try:
            # Generate embeddings
            embeddings = self.generate_embeddings(content)
            if not embeddings:
                return False
            
            # Add to Chroma collection
            doc_id = f"doc_{datetime.now().timestamp()}"
            self.collection.add(
                embeddings=[embeddings],
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings(query)
            if not query_embedding:
                return []
            
            # Search in Chroma
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            documents = []
            for i in range(len(results["documents"][0])):
                documents.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            return documents
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def generate_response(self, prompt: str, model: str = "llama3.2:1b") -> str:
        """
        Generate response using Ollama LLM
        
        Args:
            prompt: Input prompt
            model: Model to use
            
        Returns:
            Generated response
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            return "Error generating response"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def legal_rag_query(self, question: str, model: str = "llama3.2:1b") -> Dict[str, Any]:
        """
        Perform RAG-based legal query
        
        Args:
            question: Legal question
            model: LLM model to use
            
        Returns:
            Dictionary with answer and sources
        """
        # Search for relevant documents
        relevant_docs = self.search_documents(question, n_results=3)
        
        if not relevant_docs:
            return {
                "answer": "No relevant documents found in the database.",
                "sources": []
            }
        
        # Prepare context from relevant documents
        context = "\n\n".join([doc["content"][:1000] for doc in relevant_docs])
        
        # Create RAG prompt
        rag_prompt = f"""
        Based on the following legal documents, please answer the question.
        
        Context:
        {context}
        
        Question: {question}
        
        Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information, please state that clearly.
        
        Answer:
        """
        
        # Generate response
        answer = self.generate_response(rag_prompt, model)
        
        return {
            "answer": answer,
            "sources": [doc["metadata"] for doc in relevant_docs],
            "context_used": len(relevant_docs)
        }

def main():
    """Main function for testing DALI Legal AI"""
    
    print("🚀 DALI Legal AI MVP - Technical Implementation")
    print("=" * 50)
    
    # Initialize DALI system
    dali = DALILegalAI()
    
    # Check Ollama status
    print("Checking Ollama status...")
    if dali.check_ollama_status():
        print("✅ Ollama is running")
        models = dali.list_available_models()
        print(f"Available models: {models}")
    else:
        print("❌ Ollama is not running. Please start Ollama first.")
        print("Run: ollama serve")
        return
    
    # Test scraping (if API key is available)
    if dali.firecrawl_api_key:
        print("\nTesting Firecrawl scraping...")
        test_url = "https://example.com"
        result = dali.scrape_with_firecrawl(test_url)
        if "error" not in result:
            print("✅ Firecrawl is working")
        else:
            print(f"❌ Firecrawl error: {result['error']}")
    else:
        print("⚠️  Firecrawl API key not configured")
    
    # Test vector database
    print("\nTesting vector database...")
    test_content = "This is a test legal document about contract law."
    test_metadata = {"source": "test", "type": "contract", "date": "2025-01-01"}
    
    if dali.add_document_to_vectordb(test_content, test_metadata):
        print("✅ Vector database is working")
    else:
        print("❌ Vector database error")
    
    # Test search
    print("\nTesting document search...")
    search_results = dali.search_documents("contract law")
    if search_results:
        print(f"✅ Found {len(search_results)} relevant documents")
    else:
        print("❌ No search results")
    
    # Test RAG query
    print("\nTesting RAG query...")
    rag_result = dali.legal_rag_query("What is contract law?")
    print(f"Answer: {rag_result['answer'][:200]}...")
    
    print("\n🎉 DALI Legal AI MVP is ready!")

if __name__ == "__main__":
    main()

