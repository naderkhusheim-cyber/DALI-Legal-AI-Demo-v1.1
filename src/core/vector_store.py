"""
DALI Legal AI - Vector Store Module
Handles document embeddings and semantic search using Chroma
"""

import os
# Force CPU usage to avoid meta tensor/device mapping issues
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("PYTORCH_FORCE_CPU", "1")

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
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL connector not available. Using ChromaDB only.")

try:
    import torch  # type: ignore
    # Ensure torch defaults to CPU
    if hasattr(torch, "set_default_device"):
        torch.set_default_device("cpu")
except Exception:
    torch = None  # torch may not expose set_default_device on all versions

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
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model
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
        
        # Initialize embedding model (force CPU to avoid device mapping issues)
        self.embedding_model = self._init_sentence_transformer(self.embedding_model_name)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        # Initialize text splitter
        # Use larger chunk size and overlap for better Arabic context
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _init_sentence_transformer(self, model_name: str) -> SentenceTransformer:
        """Robust initialization for SentenceTransformer on CPU."""
        last_err = None
        candidates = []
        # Try given name and hub-prefixed variant
        candidates.append(model_name)
        if "/" not in model_name:
            candidates.append(f"sentence-transformers/{model_name}")
        
        for candidate in candidates:
            try:
                logger.info(f"Loading SentenceTransformer model: {candidate} on CPU")
                model = SentenceTransformer(candidate, device='cpu')
                # Warmup encode to materialize tensors off meta device
                _ = model.encode("warmup", convert_to_tensor=False)
                return model
            except Exception as e:
                last_err = e
                logger.warning(f"Load failed for '{candidate}': {e}")
        
        logger.error(f"Failed to load SentenceTransformer model '{model_name}': {last_err}")
        raise last_err
    
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

    def list_all_documents(self) -> list:
        """Return all documents and their metadata (with content preview) in the collection."""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            docs = []
            for i in range(len(results["documents"])):
                docs.append({
                    "id": results["ids"][i] if "ids" in results else None,
                    "title": results["metadatas"][i].get("title", "-"),
                    "type": results["metadatas"][i].get("document_type", "-"),
                    "source": results["metadatas"][i].get("source", "-"),
                    "content_preview": results["documents"][i][:200],
                    "metadata": results["metadatas"][i],
                })
            return docs
        except Exception as e:
            logger.error(f"Error listing all documents: {e}")
            return []


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


class MySQLVectorStore:
    """
    Per-user knowledge base using MySQL for document, chunk, and embedding storage.
    """
    def __init__(self, mysql_config):
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL connector not available")
        try:
            # Store original config for fallback connections
            self.mysql_config = mysql_config.copy()
            # Add connection pooling and timeout settings
            mysql_config.update({
                'pool_name': 'dali_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'autocommit': True,
                'connect_timeout': 10,
                'read_timeout': 10,
                'write_timeout': 10,
                'charset': 'utf8mb4',
                'use_unicode': True
            })
            self.conn = mysql.connector.connect(**mysql_config)
            self._ensure_tables()
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            raise

    def _get_connection(self):
        """Get a fresh connection from the pool"""
        try:
            # Try to get a connection from the pool
            return mysql.connector.connect(
                pool_name='dali_pool',
                pool_reset_session=True
            )
        except Exception as e:
            print(f"Failed to get connection from pool: {e}")
            # Fallback to creating a new connection
            return mysql.connector.connect(**self.mysql_config)
    
    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query with proper connection handling"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.rowcount
        except Exception as e:
            print(f"Query execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _ensure_tables(self):
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    company_name VARCHAR(255),
                    job_title VARCHAR(255),
                    employee_id VARCHAR(255),
                    phone VARCHAR(50),
                    department VARCHAR(255),
                    role VARCHAR(32) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT FALSE,
                    last_active DATETIME NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255),
                document_type VARCHAR(64),
                source VARCHAR(255),
                content LONGTEXT,
                embedding LONGBLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                shared_with_user_id INT NOT NULL,
                shared_by_user_id INT NOT NULL,
                shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (shared_by_user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    conversation_type VARCHAR(64) DEFAULT 'legal_research',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    sender_type ENUM('user', 'assistant') NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_chats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB;
            ''')
            # Optional: shared_analysis table for future
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shared_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    analysis_id INT NOT NULL,
                    shared_with_user_id INT NOT NULL,
                    shared_by_user_id INT NOT NULL,
                    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    event_type VARCHAR(64),
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB;
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def share_document(self, document_id, shared_with_user_id, shared_by_user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO shared_documents (document_id, shared_with_user_id, shared_by_user_id)
            VALUES (%s, %s, %s)
        ''', (document_id, shared_with_user_id, shared_by_user_id))
        self.conn.commit()
        cursor.close()

    def get_shared_documents(self, user_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT d.* FROM documents d
            JOIN shared_documents s ON d.id = s.document_id
            WHERE s.shared_with_user_id = %s
        ''', (user_id,))
        docs = cursor.fetchall()
        cursor.close()
        return docs

    def add_user(self, username, email, password_hash):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)
        ''', (username, email, password_hash))
        self.conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id

    def get_user_by_username(self, username):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def add_document(self, user_id, title, document_type, source, content, embedding, metadata):
        import json
        cursor = self.conn.cursor()
        metadata_str = json.dumps(metadata) if not isinstance(metadata, str) else metadata
        cursor.execute('''
            INSERT INTO documents (user_id, title, document_type, source, content, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, title, document_type, source, content, embedding.tobytes(), metadata_str))
        self.conn.commit()
        doc_id = cursor.lastrowid
        cursor.close()
        return doc_id

    def list_documents(self, user_id):
        import json
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('SELECT id, title, document_type, source, LEFT(content, 200) as content_preview, created_at FROM documents WHERE user_id=%s', (user_id,))
        docs = cursor.fetchall()
        for doc in docs:
            # Set empty metadata since column doesn't exist
            doc['metadata'] = {}
        cursor.close()
        return docs

    def search_documents(self, user_id, query_embedding, top_k=10):
        import numpy as np
        import json
        cursor = self.conn.cursor(dictionary=True)
        # Only get documents that have embeddings (not NULL)
        cursor.execute('SELECT id, title, document_type, source, content, embedding FROM documents WHERE user_id=%s AND embedding IS NOT NULL', (user_id,))
        docs = cursor.fetchall()
        for doc in docs:
            # Set empty metadata since column doesn't exist
            doc['metadata'] = {}
        cursor.close()
        scored = []
        for doc in docs:
            try:
                emb = np.frombuffer(doc['embedding'], dtype=np.float32)
                
                # Calculate cosine similarity with proper error handling
                query_norm = np.linalg.norm(query_embedding)
                emb_norm = np.linalg.norm(emb)
                
                if query_norm == 0 or emb_norm == 0:
                    sim = 0.0
                else:
                    sim = np.dot(query_embedding, emb) / (query_norm * emb_norm)
                
                # Ensure similarity score is valid
                if np.isnan(sim) or np.isinf(sim):
                    sim = 0.0
                
                doc['similarity_score'] = float(sim)  # Add similarity score to document
                scored.append((sim, doc))
            except Exception as e:
                logger.error(f"Error calculating similarity for document {doc.get('id', 'unknown')}: {str(e)}")
                doc['similarity_score'] = 0.0
                scored.append((0.0, doc))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [doc for sim, doc in scored[:top_k]]

    def create_conversation(self, user_id, title, conversation_type='legal_research'):
        """Create a new conversation"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_id, title, conversation_type)
            VALUES (%s, %s, %s)
        ''', (user_id, title, conversation_type))
        conversation_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        return conversation_id

    def get_user_conversations(self, user_id):
        """Get all conversations for a user"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE user_id = %s 
            ORDER BY updated_at DESC
        ''', (user_id,))
        conversations = cursor.fetchall()
        cursor.close()
        return conversations

    def get_conversation_messages(self, conversation_id):
        """Get all messages for a conversation"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM conversation_messages 
            WHERE conversation_id = %s 
            ORDER BY sent_at ASC
        ''', (conversation_id,))
        messages = cursor.fetchall()
        cursor.close()
        return messages

    def add_message_to_conversation(self, conversation_id, sender_type, message, metadata=None):
        """Add a message to a conversation"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_messages (conversation_id, sender_type, message, metadata)
            VALUES (%s, %s, %s, %s)
        ''', (conversation_id, sender_type, message, metadata))
        self.conn.commit()
        cursor.close()

    def update_conversation_title(self, conversation_id, new_title):
        """Update conversation title"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE conversations 
            SET title = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        ''', (new_title, conversation_id))
        self.conn.commit()
        cursor.close()

    def delete_conversation(self, conversation_id):
        """Delete a conversation and all its messages"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE id = %s', (conversation_id,))
        self.conn.commit()
        cursor.close()


if __name__ == "__main__":
    print("LOADING VECTOR STORE FROM:", __file__)
    vector_store = VectorStore()
    print("VectorStore methods:", dir(vector_store))
    all_docs = vector_store.list_all_documents()
    print(f"Found {len(all_docs)} document chunks in the collection.")
    for doc in all_docs:
        print(f"Title: {doc['title']}, Type: {doc['type']}, Source: {doc['source']}, Preview: {doc['content_preview'][:100]}")

