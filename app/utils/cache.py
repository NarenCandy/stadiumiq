"""LRU Cache utility for StadiumIQ.

This module implements a thread-safe Last Recently Used (LRU) cache using
collections.OrderedDict. It is used to cache AI assistant responses based
on user query, persona, and language.
"""

from collections import OrderedDict
import threading
from typing import Optional
from app.utils.exceptions import CacheError


class LRUCache:
    """Thread-safe Least Recently Used (LRU) Cache.

    Attributes:
        max_size: Maximum capacity of the cache.
    """

    def __init__(self, max_size: int = 128) -> None:
        """Initialize the LRU Cache.

        Args:
            max_size: Maximum number of entries before eviction.

        Raises:
            ValueError: If max_size is less than or equal to 0.
        """
        if max_size <= 0:
            raise ValueError("Cache size must be positive.")
        self.max_size: int = max_size
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._lock: threading.Lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        """Retrieve an item from the cache.

        Moves the retrieved key to the end to maintain LRU order.

        Args:
            key: The lookup key.

        Returns:
            The cached string value, or None if the key is not found.

        Raises:
            CacheError: If retrieval fails due to internal errors.
        """
        try:
            with self._lock:
                if key not in self._cache:
                    return None
                # Move to end (most recently used)
                value = self._cache.pop(key)
                self._cache[key] = value
                return value
        except Exception as e:
            raise CacheError(f"Error accessing cache: {e}") from e

    def set(self, key: str, value: str) -> None:
        """Insert or update an item in the cache.

        Evicts the oldest item if the cache exceeds its maximum size.

        Args:
            key: The cache key.
            value: The value to cache.

        Raises:
            CacheError: If insertion fails due to internal errors.
        """
        try:
            with self._lock:
                if key in self._cache:
                    self._cache.pop(key)
                elif len(self._cache) >= self.max_size:
                    # Pop first item (least recently used)
                    self._cache.popitem(last=False)
                self._cache[key] = value
        except Exception as e:
            raise CacheError(f"Error updating cache: {e}") from e

    def clear(self) -> None:
        """Clear all entries in the cache.

        Raises:
            CacheError: If clearing fails due to internal errors.
        """
        try:
            with self._lock:
                self._cache.clear()
        except Exception as e:
            raise CacheError(f"Error clearing cache: {e}") from e
