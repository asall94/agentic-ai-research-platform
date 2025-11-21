import redis
import hashlib
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, Any, List, Tuple
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Semantic caching service using Redis and sentence embeddings"""
    
    def __init__(self):
        self.enabled = settings.CACHE_ENABLED
        self.redis_client = None
        self.model = None
        
        if self.enabled:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=False
                )
                self.redis_client.ping()
                logger.info(f"Redis connected: {settings.REDIS_URL}")
                
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                logger.warning(f"Cache initialization failed: {e}. Running without cache.")
                self.enabled = False
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def _get_topic_hash(self, topic: str) -> str:
        """Generate hash for topic"""
        return hashlib.sha256(topic.lower().strip().encode()).hexdigest()[:16]
    
    def get_cached_result(
        self, 
        topic: str, 
        workflow_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for semantically similar topic
        
        Args:
            topic: Research topic
            workflow_type: Type of workflow (reflection, tool_research, multi_agent)
            
        Returns:
            Cached result dict or None
        """
        if not self.enabled:
            return None
        
        try:
            # Generate embedding for query topic
            query_embedding = self._generate_embedding(topic)
            
            # Get all cache keys for this workflow type
            pattern = f"cache:{workflow_type}:*"
            keys = self.redis_client.keys(pattern)
            
            if not keys:
                logger.debug(f"No cache entries for {workflow_type}")
                return None
            
            # Find most similar cached topic
            best_match = None
            best_similarity = 0.0
            
            for key in keys:
                try:
                    # Get cached embedding
                    embedding_key = key.decode() + ":embedding"
                    cached_embedding_bytes = self.redis_client.get(embedding_key)
                    
                    if not cached_embedding_bytes:
                        continue
                    
                    cached_embedding = np.frombuffer(cached_embedding_bytes, dtype=np.float32)
                    
                    # Compute similarity
                    similarity = self._compute_similarity(query_embedding, cached_embedding)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = key
                
                except Exception as e:
                    logger.warning(f"Error processing cache key {key}: {e}")
                    continue
            
            # Return result if similarity above threshold
            if best_match and best_similarity >= settings.CACHE_SIMILARITY_THRESHOLD:
                result_bytes = self.redis_client.get(best_match)
                if result_bytes:
                    result = json.loads(result_bytes.decode())
                    logger.info(
                        f"Cache HIT for '{topic}' (similarity: {best_similarity:.3f})"
                    )
                    return result
            
            logger.debug(
                f"Cache MISS for '{topic}' (best similarity: {best_similarity:.3f})"
            )
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    def store_result(
        self,
        topic: str,
        workflow_type: str,
        result: Dict[str, Any]
    ) -> bool:
        """
        Store workflow result with semantic embedding
        
        Args:
            topic: Research topic
            workflow_type: Type of workflow
            result: Workflow result to cache
            
        Returns:
            True if stored successfully
        """
        if not self.enabled:
            return False
        
        try:
            # Generate embedding
            embedding = self._generate_embedding(topic)
            
            # Create cache key
            topic_hash = self._get_topic_hash(topic)
            cache_key = f"cache:{workflow_type}:{topic_hash}"
            embedding_key = f"{cache_key}:embedding"
            
            # Store result
            self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SECONDS,
                json.dumps(result)
            )
            
            # Store embedding
            self.redis_client.setex(
                embedding_key,
                settings.CACHE_TTL_SECONDS,
                embedding.astype(np.float32).tobytes()
            )
            
            logger.info(f"Cached result for '{topic}' ({workflow_type})")
            return True
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            return False
    
    def invalidate_cache(self, topic_hash: Optional[str] = None) -> int:
        """
        Invalidate cache entries
        
        Args:
            topic_hash: Specific topic hash to invalidate, or None for all
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            if topic_hash:
                # Delete specific entry
                pattern = f"cache:*:{topic_hash}*"
            else:
                # Delete all cache entries
                pattern = "cache:*"
            
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("cache:*")
            
            # Count by workflow type
            counts = {
                "reflection": 0,
                "tool_research": 0,
                "multi_agent": 0
            }
            
            for key in keys:
                key_str = key.decode()
                for wf_type in counts.keys():
                    if f":{wf_type}:" in key_str:
                        counts[wf_type] += 1
            
            return {
                "enabled": True,
                "total_entries": len(keys) // 2,  # Each entry has embedding
                "by_workflow": counts,
                "redis_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "ttl_days": settings.CACHE_TTL_SECONDS // 86400
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache instance
cache_service = CacheService()
