"""User Passport — per-user savings tracker."""

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class UserStats:
    """Per-user cache and environmental savings stats."""
    user_id: str
    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    tokens_saved: int = 0
    water_saved_ml: float = 0.0
    energy_saved_wh: float = 0.0
    carbon_saved_g: float = 0.0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    @property
    def hit_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return self.cache_hits / self.total_queries

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(self.hit_rate, 3),
            "tokens_saved": self.tokens_saved,
            "water_saved_ml": round(self.water_saved_ml, 4),
            "energy_saved_wh": round(self.energy_saved_wh, 6),
            "carbon_saved_g": round(self.carbon_saved_g, 4),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


class UserPassport:
    """In-memory per-user savings registry."""

    def __init__(self) -> None:
        self._users: Dict[str, UserStats] = {}

    def get_or_create(self, user_id: str) -> UserStats:
        if user_id not in self._users:
            self._users[user_id] = UserStats(user_id=user_id)
        return self._users[user_id]

    def record(
        self,
        user_id: str,
        cache_hit: bool,
        tokens_saved: int = 0,
        water_saved_ml: float = 0.0,
        energy_saved_wh: float = 0.0,
        carbon_saved_g: float = 0.0,
    ) -> UserStats:
        stats = self.get_or_create(user_id)
        stats.total_queries += 1
        stats.last_seen = time.time()
        if cache_hit:
            stats.cache_hits += 1
            stats.tokens_saved += tokens_saved
            stats.water_saved_ml += water_saved_ml
            stats.energy_saved_wh += energy_saved_wh
            stats.carbon_saved_g += carbon_saved_g
        else:
            stats.cache_misses += 1
        return stats

    def get(self, user_id: str) -> dict | None:
        if user_id not in self._users:
            return None
        return self._users[user_id].to_dict()

    def all_users(self) -> list[dict]:
        return [u.to_dict() for u in self._users.values()]

    def leaderboard(self, top_n: int = 10) -> list[dict]:
        sorted_users = sorted(
            self._users.values(),
            key=lambda u: u.water_saved_ml,
            reverse=True
        )
        return [u.to_dict() for u in sorted_users[:top_n]]


# Global singleton
_passport: UserPassport | None = None


def get_passport() -> UserPassport:
    global _passport
    if _passport is None:
        _passport = UserPassport()
    return _passport
