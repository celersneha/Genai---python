### Data Ingestion

## Document datastructure

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

doc = Document(
    page_content="this is the main text content I am using to create RAG.",
    metadata={
        "source": "example.txt",
        "pages":1,
        "author":"Sneha Sharma",
        "date_created":"2026-05-27"
    }
)

print(doc)

## Create a simple txt file
import os
os.makedirs("data/text_files", exist_ok=True)

sample_texts = {
    "data/text_files/python_intro.txt": """
Python is a high-level programming language known for its simplicity and readability.

Key Features:
- Easy to learn
- Large standard library
- Cross-platform support
- Strong community

Applications:
- Web Development
- Data Science & AI
- Automation
- Backend Development
"""
}

for filepath, content in sample_texts.items():
    with open(filepath,'w',encoding='utf-8') as f:
        f.write(content)
        
print("✅Sample text file created")

## Textload
loader = TextLoader("data/text_files/python_intro.txt",encoding="utf-8")

doc = loader.load()
# print(doc)

# create chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Create chunks
chunks = text_splitter.split_documents(doc)

# Directory Loader
dir_loader = DirectoryLoader(
    "data/text_files",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={'encoding' : 'utf-8'},
    show_progress=False
)

# docs = dir_loader.load()
# print(docs)

# Pdf loader
pdf_loader = DirectoryLoader(
    "data/pdf",
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=False
)

pdf_doc = pdf_loader.load()
# print(pdf_doc)

chunks = text_splitter.split_documents(pdf_doc)

### embedding and vectore store db
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingManager:
    """Handles document embdding generation using sentence transformer"""
    
    def __init__(self, model_name:str ="all-MiniLM-L6-v2"):
        """
        Initializes the embedding manager.
        
        Args:
            model_name: Hugging Face model name for sentence embeddings
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load the SentenceTransformer Model"""
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model loaded succesfully. Embedding dimeension:{self.model.get_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model {self.model_name}:{e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        print(f"Generate embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Generate embeddings with shape: {embeddings.shape}")
        return embeddings
        
# initialize embedding manager
embedding_manager = EmbeddingManager()

class VectorStore:
    """
    Manages document embeddings in a ChromaDB vector store
    """
    
    def __init__(self, collection_name: str = "pdf_documents", persist_dictionary: str = "data/vector_store"):
        """
        Initialize the vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_dictionary: Directory to persist the vector store
        """
        self.collection_name = collection_name
        self.persist_dictionary = persist_dictionary
        self.client= None
        self.collection = None
        self._initialize_store()
        
    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            # create persistent ChromaDB client
            os.makedirs(self.persist_dictionary, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_dictionary)
            
            #Get or create collection
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name,
                metadata={"description":"PDF documents embedding for RAG"} 
            )
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing docs in collection: {self.collection.count()}")
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise
        
    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        """
        Add documents and their embeddings to the vector store
        
        Args:
            documents: List of langchain documents
            embeddings: Corresponding emneddings for the documents
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        print(f"Adding {len(documents) } to the vector store")
        
        # prepare the data for ChromaDB
        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []
        
        for i, (doc,embedding) in enumerate(zip(documents,embeddings)):
            # generate unique id
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)
            
            #prepare metadata
            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)
            
            # document content
            documents_text.append(doc.page_content)
            
            # embedding
            embeddings_list.append(embedding.tolist())
            
            
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Succesfully added {len(documents)} documents to vector db")
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise
        
vector_store = VectorStore()

# convert the text to embedding
texts=[doc.page_content for doc in chunks]
# print(texts)

## generate the embedding
embeddings = embedding_manager.generate_embeddings(texts)

## store in the vector db
vector_store.add_documents(chunks, embeddings)

#-----------------------------------
### Rag retriever pipeline
class RagRetriever:
    """Handles query-based retrieval from the vector store"""
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager ):
        """
        initializes the retriever
        
        Args:
            vector_store: Vector Store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
        
    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        retrieve relevant documents for a query
        
        Args:
            query: the search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
        
        Returns:
            List of dictionaries retrieved documents and metadata
        """
        print(f"Retrieving documents for query: '{query}")
        print(f"Top K: {top_k}, Score threshold: {score_threshold}")
        
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]
        
        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # Process results
            retrieved_docs = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]
                
                for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):
                    similarity_score = 1 - distance
                    
                    if similarity_score >= score_threshold:
                        retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i+1
                        })
                        
                print(f"Retrieved {len(retrieved_docs)} documents (after filtering)")
            else:
                print("No docs found")
                
            return retrieved_docs
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
        
rag_retriever = RagRetriever(vector_store, embedding_manager)
res = rag_retriever.retrieve("what is the tech stack of calmhive?")
print(f"🔍Result: \n\n{res}")