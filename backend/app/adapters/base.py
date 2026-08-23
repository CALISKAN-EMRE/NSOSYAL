from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.post import Post, Author
from app.models.topic import Topic


class DataSourceAdapter(ABC):
    """Abstract data source adapter interface for NSosyal Pusula.

    This interface decouples the core intelligence layer from the underlying data source.
    In Phase 1, it is implemented by JsonDemoAdapter. In future phases, it can be implemented
    by an authorized platform REST/WebSocket API adapter without changing business logic.
    """

    @abstractmethod
    def get_posts(
        self,
        topic_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Post]:
        """Retrieve a list of posts with optional filtering."""
        pass

    @abstractmethod
    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """Retrieve a single post by ID."""
        pass

    @abstractmethod
    def get_posts_by_ids(self, post_ids: List[str]) -> List[Post]:
        """Retrieve a list of posts by their IDs."""
        pass

    @abstractmethod
    def get_topics(self) -> List[Topic]:
        """Retrieve all active discussion topics with aggregated stats."""
        pass

    @abstractmethod
    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """Retrieve a topic by ID."""
        pass

    @abstractmethod
    def get_authors(self) -> List[Author]:
        """Retrieve unique authors."""
        pass

    @abstractmethod
    def health_check(self) -> dict:
        """Return adapter connectivity and health metadata."""
        pass
