from fastapi import Depends
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService


# Use singleton pattern to ensure we only create one instance
_vector_store_instance = None
_llm_service_instance = None
_memory_service_instance = None
_rag_service_instance = None


def get_vector_store():
    """Return a singleton instance of VectorStoreService"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    return _vector_store_instance


def get_llm_service():
    """Return a singleton instance of LLMService"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance


def get_memory_service():
    """Return a singleton instance of MemoryService"""
    global _memory_service_instance
    if _memory_service_instance is None:
        vector_store = get_vector_store()
        llm_service = get_llm_service()
        _memory_service_instance = MemoryService(vector_store, llm_service)
    return _memory_service_instance


def get_rag_service():
    """Return a singleton instance of RAGService"""
    global _rag_service_instance
    if _rag_service_instance is None:
        vector_store = get_vector_store()
        memory_service = get_memory_service()
        llm_service = get_llm_service()
        _rag_service_instance = RAGService(vector_store, memory_service, llm_service)
    return _rag_service_instance