# ============================================================
#  services/mediscan_rag_service.py
#  RAG system for MediScan using local embeddings and ChromaDB
# ============================================================

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from services.bytez_client import call_bytez

logger = logging.getLogger("mediscan_rag")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PERSIST_DIR = BASE_DIR / "mediscan_vectordb"
PDF_DATA_DIR = BASE_DIR / "medicine_pdf"

# Collection name for medicine data
COLLECTION_NAME = "medicine_knowledge"


class MediScanRAGService:
    """RAG service for medicine information retrieval"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialized = False
        self._medicine_names: List[str] = []
    
    def initialize(self):
        """Initialize the RAG system with local embeddings and ChromaDB"""
        if self._initialized:
            return
        
        try:
            # Load local embedding model (all-MiniLM-L6-v2 is fast and good)
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB with persistence
            logger.info(f"Initializing ChromaDB at {CHROMA_PERSIST_DIR}")
            CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_PERSIST_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Medicine information from PDFs"}
            )
            
            # Load medicine names for autocomplete
            self._load_medicine_names()
            
            self._initialized = True
            logger.info(f"MediScan RAG initialized. {self.collection.count()} documents in collection.")
            
        except Exception as e:
            logger.error(f"Failed to initialize MediScan RAG: {e}")
            raise
    
    def _load_medicine_names(self):
        """Load all medicine names from the collection for autocomplete"""
        if self.collection and self.collection.count() > 0:
            results = self.collection.get(include=["metadatas"])
            self._medicine_names = list(set(
                meta.get("medicine_name", "") 
                for meta in results.get("metadatas", [])
                if meta.get("medicine_name")
            ))
            logger.info(f"Loaded {len(self._medicine_names)} medicine names for autocomplete")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using local model"""
        if not self.embedding_model:
            self.initialize()
        return self.embedding_model.encode(text).tolist()
    
    def add_medicine_document(self, medicine_name: str, content: str, metadata: Optional[Dict] = None):
        """Add a medicine document to the vector database"""
        if not self._initialized:
            self.initialize()
        
        # Create document ID from medicine name
        doc_id = re.sub(r'[^a-zA-Z0-9]', '_', medicine_name.lower())
        
        # Generate embedding
        embedding = self.get_embedding(f"{medicine_name} {content}")
        
        # Prepare metadata
        doc_metadata = {
            "medicine_name": medicine_name,
            "source": "pdf",
            **(metadata or {})
        }
        
        # Add to collection
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[doc_metadata]
        )
        
        # Update medicine names list
        if medicine_name not in self._medicine_names:
            self._medicine_names.append(medicine_name)
        
        logger.info(f"Added/updated medicine: {medicine_name}")
    
    def search_medicines(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for medicines in the vector database"""
        if not self._initialized:
            self.initialize()
        
        if self.collection.count() == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.get_embedding(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        medicines = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
            distance = results.get("distances", [[]])[0][i] if results.get("distances") else 0
            medicines.append({
                "medicine_name": metadata.get("medicine_name", "Unknown"),
                "content": doc,
                "metadata": metadata,
                "similarity": 1 - distance  # Convert distance to similarity
            })
        
        return medicines
    
    def suggest_medicines(self, partial_query: str, limit: int = 10) -> List[str]:
        """Suggest medicine names based on partial input (for autocomplete)"""
        if not self._initialized:
            self.initialize()
        
        if not partial_query:
            return self._medicine_names[:limit]
        
        query_lower = partial_query.lower()
        
        # Exact prefix matches first
        prefix_matches = [
            name for name in self._medicine_names 
            if name.lower().startswith(query_lower)
        ]
        
        # Then fuzzy matches (contains)
        contains_matches = [
            name for name in self._medicine_names 
            if query_lower in name.lower() and name not in prefix_matches
        ]
        
        # Combine and limit
        suggestions = prefix_matches + contains_matches
        return suggestions[:limit]
    
    def generate_medicine_info(self, medicine_name: str) -> str:
        """Generate medicine information using RAG + LLM"""
        if not self._initialized:
            self.initialize()
        
        # Search for relevant documents
        search_results = self.search_medicines(medicine_name, n_results=3)
        
        if not search_results:
            # No data in vector DB, use LLM only
            return self._generate_with_llm_only(medicine_name)
        
        # Build context from search results
        context_parts = []
        for result in search_results:
            if result["similarity"] > 0.3:  # Only use relevant results
                context_parts.append(f"Medicine: {result['medicine_name']}\n{result['content']}")
        
        if not context_parts:
            return self._generate_with_llm_only(medicine_name)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate response using LLM with context
        prompt = f"""You are a professional medical assistant. Based on the following medicine information from our database, provide accurate details about "{medicine_name}".

DATABASE INFORMATION:
{context}

IMPORTANT RULES:
1. Use the database information as the primary source
2. If the exact medicine is found, use that information
3. If similar medicines are found, mention the closest match
4. Fill in any missing sections with general medical knowledge
5. DO NOT include "Source of Information" labels in your response

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

Medicine Name:
[Full medicine name with composition if available]

Use:
[What the medicine is used for]

Dosage:
[Dosage information]

Precautions:
[Precautions and warnings]

Common Side Effects:
[List of common side effects]

Disclaimer:
This information is for educational purposes only. Consult a doctor before taking any medication."""

        response = call_bytez(prompt, temperature=0.3, max_tokens=2048)
        
        if response:
            return response
        else:
            return self._format_from_search_results(search_results[0])
    
    def _generate_with_llm_only(self, medicine_name: str) -> str:
        """Generate medicine info using LLM only (no RAG context)"""
        prompt = f"""You are a professional medical assistant. Provide accurate information about the medicine "{medicine_name}".

IMPORTANT: DO NOT include "Source of Information" labels in your response.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

Medicine Name:
{medicine_name}

Use:
[What the medicine is used for - from general medical knowledge]

Dosage:
[General dosage information - always recommend consulting a doctor]

Precautions:
[Important precautions and warnings]

Common Side Effects:
[List of common side effects]

Disclaimer:
This information is for educational purposes only. Consult a doctor before taking any medication."""

        response = call_bytez(prompt, temperature=0.3, max_tokens=2048)
        
        if response:
            return response
        else:
            return f"""Medicine Name:
{medicine_name}

Use:
Information not available. Please consult a healthcare professional.

Dosage:
As directed by the Physician.

Precautions:
Consult a doctor before taking any medication.

Common Side Effects:
Information not available.

Disclaimer:
This information is for educational purposes only. Consult a doctor before taking any medication."""
    
    def _format_from_search_results(self, result: Dict) -> str:
        """Format search result into standard output format"""
        return f"""Medicine Name:
{result.get('medicine_name', 'Unknown')}

{result.get('content', 'Information not available.')}

Disclaimer:
This information is for educational purposes only. Consult a doctor before taking any medication."""
    
    def ingest_pdf(self, pdf_path: str) -> int:
        """Ingest a PDF file and add medicines to the vector database"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF not installed. Run: pip install pymupdf")
            return 0
        
        if not self._initialized:
            self.initialize()
        
        count = 0
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text()
            
            doc.close()
            
            # Parse medicines from the PDF text
            medicines = self._parse_medicines_from_text(full_text)
            
            for medicine_name, content in medicines.items():
                self.add_medicine_document(medicine_name, content)
                count += 1
            
            logger.info(f"Ingested {count} medicines from {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {pdf_path}: {e}")
        
        return count
    
    def _parse_medicines_from_text(self, text: str) -> Dict[str, str]:
        """Parse medicine information from PDF text"""
        medicines = {}
        
        # Split by common medicine section patterns
        # This is a basic parser - adjust based on your PDF format
        sections = re.split(r'\n(?=Medicine Name:|MEDICINE NAME:|Drug Name:)', text, flags=re.IGNORECASE)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Try to extract medicine name
            name_match = re.search(r'(?:Medicine Name|MEDICINE NAME|Drug Name)[:\s]*([^\n]+)', section, re.IGNORECASE)
            if name_match:
                medicine_name = name_match.group(1).strip()
                # Clean up the content
                content = section.strip()
                medicines[medicine_name] = content
        
        # If no structured format found, treat entire text as one document
        if not medicines and text.strip():
            # Try to find any medicine-like names in the text
            lines = text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                if len(line.strip()) > 3 and len(line.strip()) < 100:
                    medicines[line.strip()] = text
                    break
        
        return medicines
    
    def bulk_add_medicines(self, medicines_data: List[Dict]):
        """Bulk add medicines to the vector database
        
        Each dict should have:
        - medicine_name: str
        - use: str (optional)
        - dosage: str (optional)
        - precautions: str (optional)
        - side_effects: str (optional)
        """
        if not self._initialized:
            self.initialize()
        
        for med in medicines_data:
            name = med.get("medicine_name", "")
            if not name:
                continue
            
            # Build content string
            content_parts = []
            if med.get("use"):
                content_parts.append(f"Use:\n{med['use']}")
            if med.get("dosage"):
                content_parts.append(f"Dosage:\n{med['dosage']}")
            if med.get("precautions"):
                content_parts.append(f"Precautions:\n{med['precautions']}")
            if med.get("side_effects"):
                content_parts.append(f"Common Side Effects:\n{med['side_effects']}")
            
            content = "\n\n".join(content_parts) if content_parts else "No detailed information available."
            
            self.add_medicine_document(name, content, med.get("metadata"))
        
        logger.info(f"Bulk added {len(medicines_data)} medicines")


# Global instance
mediscan_rag = MediScanRAGService()


def get_mediscan_rag() -> MediScanRAGService:
    """Get the global MediScan RAG service instance"""
    if not mediscan_rag._initialized:
        mediscan_rag.initialize()
    return mediscan_rag
