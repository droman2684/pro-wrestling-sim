from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, JSON, ForeignKey, Float
from typing import List, Optional

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class WrestlerModel(db.Model):
    __tablename__ = 'wrestlers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100))
    billing_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Store nested attributes as JSON to maintain flexibility and compatibility
    bio: Mapped[dict] = mapped_column(JSON, default={})
    physical: Mapped[dict] = mapped_column(JSON, default={})
    offense: Mapped[dict] = mapped_column(JSON, default={})
    defense: Mapped[dict] = mapped_column(JSON, default={})
    entertainment: Mapped[dict] = mapped_column(JSON, default={})
    intangibles: Mapped[dict] = mapped_column(JSON, default={})
    styles: Mapped[dict] = mapped_column(JSON, default={})
    moves: Mapped[dict] = mapped_column(JSON, default={})
    status: Mapped[dict] = mapped_column(JSON, default={})
    contract: Mapped[dict] = mapped_column(JSON, default={})

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "billing_name": self.billing_name,
            "bio": self.bio,
            "physical": self.physical,
            "offense": self.offense,
            "defense": self.defense,
            "entertainment": self.entertainment,
            "intangibles": self.intangibles,
            "styles": self.styles,
            "moves": self.moves,
            "status": self.status,
            "contract": self.contract
        }

class TitleModel(db.Model):
    __tablename__ = 'titles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prestige: Mapped[int] = mapped_column(Integer, default=50)
    current_holder_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "prestige": self.prestige,
            "current_holder_id": self.current_holder_id
        }

class BrandModel(db.Model):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(20), default="#000000")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Store relationships as JSON lists of IDs for now to mimic current structure
    assigned_titles: Mapped[list] = mapped_column(JSON, default=[])
    assigned_wrestlers: Mapped[list] = mapped_column(JSON, default=[])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "color": self.color,
            "assigned_titles": self.assigned_titles,
            "assigned_wrestlers": self.assigned_wrestlers,
            "is_active": self.is_active
        }

class TagTeamModel(db.Model):
    __tablename__ = 'tag_teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    member_ids: Mapped[list] = mapped_column(JSON, default=[])
    chemistry: Mapped[int] = mapped_column(Integer, default=50)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "member_ids": self.member_ids,
            "chemistry": self.chemistry,
            "wins": self.wins,
            "losses": self.losses,
            "is_active": self.is_active
        }

class FeudModel(db.Model):
    __tablename__ = 'feuds'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wrestler_a_id: Mapped[int] = mapped_column(Integer, nullable=False)
    wrestler_b_id: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[str] = mapped_column(String(50), default="heated")
    matches_remaining: Mapped[int] = mapped_column(Integer, default=3)
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    wins_a: Mapped[int] = mapped_column(Integer, default=0)
    wins_b: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    blowoff_match_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "wrestler_a_id": self.wrestler_a_id,
            "wrestler_b_id": self.wrestler_b_id,
            "intensity": self.intensity,
            "matches_remaining": self.matches_remaining,
            "total_matches": self.total_matches,
            "wins_a": self.wins_a,
            "wins_b": self.wins_b,
            "is_active": self.is_active,
            "blowoff_match_scheduled": self.blowoff_match_scheduled
        }

class StableModel(db.Model):
    __tablename__ = 'stables'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    leader_id: Mapped[int] = mapped_column(Integer, nullable=False)
    member_ids: Mapped[list] = mapped_column(JSON, default=[])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "is_active": self.is_active
        }

# Models for Game State and Calendar could also be added, or stored as single row configuration tables.
class GameStateModel(db.Model):
    __tablename__ = 'game_state'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True) # Singleton row, ID=1
    save_name: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer, default=1)
    month: Mapped[int] = mapped_column(Integer, default=1)
    week: Mapped[int] = mapped_column(Integer, default=1)
    
    # Store other global state objects as JSON blobs for simplicity in migration
    company_data: Mapped[dict] = mapped_column(JSON, default={})
    calendar_data: Mapped[dict] = mapped_column(JSON, default={})
    records_data: Mapped[dict] = mapped_column(JSON, default={})
