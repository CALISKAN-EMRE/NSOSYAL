import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.adapters.base import DataSourceAdapter
from app.models.post import Post, Author
from app.models.topic import Topic

logger = logging.getLogger(__name__)


class JsonDemoAdapter(DataSourceAdapter):
    """Concrete data source adapter that reads synthetic demo posts from a local JSON file."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self._posts_cache: List[Post] = []
        self._topics_cache: Dict[str, Topic] = {}
        self._authors_cache: Dict[str, Author] = {}
        self.load_data()

    def load_data(self) -> None:
        """Load and parse demo posts from the configured JSON file."""
        if not self.data_path.exists():
            # Fallback path lookup in case working directory differs
            alt_path = Path("..") / "data" / "demo_posts.json"
            if alt_path.exists():
                self.data_path = alt_path
            else:
                logger.error(f"Demo data file not found at: {self.data_path}")
                self._posts_cache = []
                self._topics_cache = {}
                return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self._posts_cache = [Post.model_validate(p) for p in raw_data]
            self._reindex_metadata()
            logger.info(
                f"Successfully loaded {len(self._posts_cache)} demo posts from {self.data_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load or parse JSON demo data: {e}", exc_info=True)
            self._posts_cache = []

    def _reindex_metadata(self) -> None:
        """Aggregate topics, statistics, and authors from cached posts."""
        topics_map: Dict[str, dict] = {}
        authors_map: Dict[str, Author] = {}

        for post in self._posts_cache:
            authors_map[post.author.id] = post.author

            if post.topic_id not in topics_map:
                topics_map[post.topic_id] = {
                    "id": post.topic_id,
                    "title": post.topic_title,
                    "posts": [],
                    "authors": set(),
                    "tags": set(),
                    "last_activity": post.created_at,
                }
            topics_map[post.topic_id]["posts"].append(post)
            topics_map[post.topic_id]["authors"].add(post.author.id)
            topics_map[post.topic_id]["tags"].update(post.tags)
            if post.created_at > topics_map[post.topic_id]["last_activity"]:
                topics_map[post.topic_id]["last_activity"] = post.created_at

        self._topics_cache = {}
        for t_id, t_info in topics_map.items():
            self._topics_cache[t_id] = Topic(
                id=t_id,
                title=t_info["title"],
                description=f"{t_info['title']} başlığında paylaşılan görüşler ve tartışma akışı.",
                post_count=len(t_info["posts"]),
                participant_count=len(t_info["authors"]),
                tags=sorted(list(t_info["tags"])),
                last_activity=t_info["last_activity"],
            )

        self._authors_cache = authors_map

    def get_posts(
        self,
        topic_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Post]:
        results = self._posts_cache

        if topic_id:
            results = [p for p in results if p.topic_id == topic_id]

        if search:
            query = search.lower().strip()
            results = [
                p
                for p in results
                if query in p.text.lower()
                or query in p.author.name.lower()
                or query in p.author.handle.lower()
                or any(query in tag.lower() for tag in p.tags)
            ]

        # Sort by creation time descending by default
        results = sorted(results, key=lambda x: x.created_at, reverse=True)
        return results[offset : offset + limit]

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        for post in self._posts_cache:
            if post.id == post_id:
                return post
        return None

    def get_posts_by_ids(self, post_ids: List[str]) -> List[Post]:
        id_set = set(post_ids)
        return [p for p in self._posts_cache if p.id in id_set]

    def get_topics(self) -> List[Topic]:
        return sorted(
            list(self._topics_cache.values()),
            key=lambda t: t.post_count,
            reverse=True,
        )

    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        return self._topics_cache.get(topic_id)

    def get_authors(self) -> List[Author]:
        return list(self._authors_cache.values())

    def health_check(self) -> dict:
        return {
            "adapter_type": "json_demo",
            "file_path": str(self.data_path),
            "file_exists": self.data_path.exists(),
            "cached_posts_count": len(self._posts_cache),
            "cached_topics_count": len(self._topics_cache),
            "status": "healthy" if len(self._posts_cache) > 0 else "degraded",
        }
