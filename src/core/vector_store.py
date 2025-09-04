"""
DALI Legal AI - Vector Store Module
Handles document embeddings and semantic search using Chroma
"""

import os
import logging
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector Store for DALI Legal AI System
    Manages document embeddings and semantic search using Chroma
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/embeddings",
        collection_name: str = "legal_documents",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            # Create new collection
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "DALI Legal AI document embeddings"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using SentenceTransformer"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _generate_document_id(self, content: str, metadata: Dict) -> str:
        """Generate unique ID for document based on content and metadata"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        source = metadata.get('source', 'unknown')
        return f"{source}_{content_hash[:8]}"
    
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        chunk_documents: bool = True
    ) -> List[str]:
        """
        Add a document to the vector store
        
        Args:
            content: Document text content
            metadata: Document metadata (source, title, etc.)
            chunk_documents: Whether to split document into chunks
            
        Returns:
            List of document IDs that were added
        """
        if metadata is None:
            metadata = {}
        
        try:
            if chunk_documents:
                # Split document into chunks
                chunks = self.text_splitter.split_text(content)
                document_ids = []
                
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    
                    doc_id = self._generate_document_id(chunk, chunk_metadata)
                    embedding = self._generate_embedding(chunk)
                    
                    self.collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[chunk_metadata],
                        ids=[doc_id]
                    )
                    
                    document_ids.append(doc_id)
                
                logger.info(f"Added document with {len(chunks)} chunks")
                return document_ids
            
            else:
                # Add entire document as single entry
                doc_id = self._generate_document_id(content, metadata)
                embedding = self._generate_embedding(content)
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                logger.info(f"Added single document: {doc_id}")
                return [doc_id]
                
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def add_documents_batch(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add multiple documents in batches
        
        Args:
            documents: List of LangChain Document objects
            batch_size: Number of documents to process in each batch
            
        Returns:
            List of all document IDs that were added
        """
        all_document_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_ids = []
            batch_embeddings = []
            batch_contents = []
            batch_metadatas = []
            
            for doc in batch:
                doc_id = self._generate_document_id(doc.page_content, doc.metadata)
                embedding = self._generate_embedding(doc.page_content)
                
                batch_ids.append(doc_id)
                batch_embeddings.append(embedding)
                batch_contents.append(doc.page_content)
                batch_metadatas.append(doc.metadata)
            
            try:
                self.collection.add(
                    embeddings=batch_embeddings,
                    documents=batch_contents,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
                all_document_ids.extend(batch_ids)
                logger.info(f"Added batch of {len(batch)} documents")
                
            except Exception as e:
                logger.error(f"Error adding document batch: {e}")
                raise
        
        return all_document_ids
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Metadata filters to apply
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            search_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            if filter_metadata:
                search_kwargs["where"] = filter_metadata
            
            results = self.collection.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'id': results['ids'][0][i] if 'ids' in results else None
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def search_by_document_type(
        self,
        query: str,
        document_type: str,
        n_results: int = 5
    ) -> List[Dict]:
        """Search for documents of a specific type"""
        filter_metadata = {"document_type": document_type}
        return self.search(query, n_results, filter_metadata)
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        try:
            results = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            if results['documents']:
                return {
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0],
                    'id': document_id
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def delete_documents_by_source(self, source: str) -> int:
        """Delete all documents from a specific source"""
        try:
            results = self.collection.get(
                where={"source": source},
                include=["documents"]
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} documents from source: {source}")
                return len(results['ids'])
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting documents from source {source}: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            # Get sample of metadata to analyze document types
            sample_results = self.collection.get(
                limit=min(100, count),
                include=["metadatas"]
            )
            
            document_types = {}
            sources = {}
            
            for metadata in sample_results['metadatas']:
                doc_type = metadata.get('document_type', 'unknown')
                source = metadata.get('source', 'unknown')
                
                document_types[doc_type] = document_types.get(doc_type, 0) + 1
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'total_documents': count,
                'document_types': document_types,
                'sources': sources,
                'embedding_model': self.embedding_model_name,
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def similarity_search_with_score_threshold(
        self,
        query: str,
        score_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict]:
        """Search with minimum similarity score threshold"""
        results = self.search(query, n_results=max_results)
        return [r for r in results if r['score'] >= score_threshold]
    
    def reset_collection(self) -> bool:
        """Reset the entire collection (delete all documents)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "DALI Legal AI document embeddings"}
            )
            logger.info(f"Reset collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


# Utility functions
def create_legal_document_metadata(
    title: str,
    document_type: str,
    source: str,
    date_created: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    practice_area: Optional[str] = None,
    **kwargs
) -> Dict:
    """Create standardized metadata for legal documents"""
    metadata = {
        'title': title,
        'document_type': document_type,
        'source': source,
        'date_created': date_created,
        'jurisdiction': jurisdiction,
        'practice_area': practice_area
    }
    
    # Add any additional metadata
    metadata.update(kwargs)
    
    # Remove None values
    return {k: v for k, v in metadata.items() if v is not None}


if __name__ == "__main__":
    # Example usage
    vector_store = VectorStore()
    
    # Test adding a document
    sample_doc = """
    This is a sample legal contract between Party A and Party B.
    The contract outlines the terms and conditions for the provision of legal services.
    """
    
    metadata = create_legal_document_metadata(
        title="Sample Legal Contract",
        document_type="contract",
        source="test_document",
        jurisdiction="Saudi Arabia",
        practice_area="commercial_law"
    )
    
    doc_ids = vector_store.add_document(sample_doc, metadata)
    print(f"Added document with IDs: {doc_ids}")
    
    # Test search
    results = vector_store.search("legal services contract")
    print(f"Search results: {len(results)}")
    
    # Get collection stats
    stats = vector_store.get_collection_stats()
    print(f"Collection stats: {stats}")

