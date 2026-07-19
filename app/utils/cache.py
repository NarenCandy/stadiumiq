"""LRU Cache utility for StadiumIQ.

This module implements a thread-safe Least Recently Used (LRU) cache backed by
collections.OrderedDict.  It is used by the chat route to cache AI assistant
responses keyed on (persona, language, message) so repeated identical queries
are served without a Groq API round-trip.

Main exports:
    LRUCache

Typical usage example:
    from app.utils.cache import LRUCache
    cache = LRUCache(max_size=128)
    cache.set("key", "value")
    cached_value = cache.get("key")
"""

import logging
import threading
from collections import OrderedDict
from typing import Optional

from app.constants import CACHE_SIZE
from app.utils.exceptions import CacheError

logger: logging.Logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe Least Recently Used (LRU) cache.

    Uses an OrderedDict to maintain insertion order so that the least recently
    used entry can be evicted in O(1) time when the cache reaches capacity.

    Attributes:
        max_size: Maximum number of entries the cache can hold before eviction.
    """

    def __init__(self, max_size: int = CACHE_SIZE) -> None:
        """Initialise the LRU cache with a fixed capacity.

        Args:
            max_size: Maximum number of entries before the oldest is evicted.
                Must be a positive integer.

        Raises:
            ValueError: If max_size is not a positive integer.
        """
        if max_size <= 0:
            raise ValueError("Cache size must be positive.")
        self.max_size: int = max_size
        self._store: OrderedDict[str, str] = OrderedDict()
        self._lock: threading.Lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        """Retrieve a cached value by key and mark it as most recently used.

        Args:
            key: The string lookup key.

        Returns:
            The cached string value, or None if the key is absent.

        Raises:
            CacheError: If an unexpected error occurs during retrieval.
        """
        try:
            with self._lock:
                if key not in self._store:
                    return None
                cached_value = self._store.pop(key)
                self._store[key] = cached_value
                return cached_value
        except Exception as cache_error:
            logger.error("Cache get failed for key=%s: %s", key, cache_error)
            raise CacheError(f"Error accessing cache: {cache_error}") from cache_error

    def set(self, key: str, value: str) -> None:
        """Insert or update a value in the cache.

        Evicts the least recently used entry when the cache is at capacity.

        Args:
            key: The string cache key.
            value: The string value to store.

        Raises:
            CacheError: If an unexpected error occurs during insertion.
        """
        try:
            with self._lock:
                if key in self._store:
                    self._store.pop(key)
                elif len(self._store) >= self.max_size:
                    self._store.popitem(last=False)
                self._store[key] = value
        except Exception as cache_error:
            logger.error("Cache set failed for key=%s: %s", key, cache_error)
            raise CacheError(f"Error updating cache: {cache_error}") from cache_error

    def clear(self) -> None:
        """Remove all entries from the cache.

        Raises:
            CacheError: If an unexpected error occurs during the clear operation.
        """
        try:
            with self._lock:
                self._store.clear()
        except Exception as cache_error:
            logger.error("Cache clear failed: %s", cache_error)
            raise CacheError(f"Error clearing cache: {cache_error}") from cache_error
