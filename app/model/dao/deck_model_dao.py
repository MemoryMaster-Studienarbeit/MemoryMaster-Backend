from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String, unique=True, nullable=True)

    # Relationship to decks
    decks = relationship("Deck", back_populates="session", cascade="all, delete-orphan")


# Define the Deck model
class Deck(Base):
    __tablename__ = "decks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_name = Column(String, nullable=False)
    session_uuid = Column(String, ForeignKey("sessions.session_uuid"), nullable=True)

    # Relationship to cards
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")
    session = relationship("Session", back_populates="decks")


# Define the Card model
class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_uuid = Column(String, nullable=False)
    card_front = Column(Text, nullable=False)
    card_back = Column(Text, nullable=False)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=True)
    last_learned = Column(String, nullable=False, default="")
    next_learned = Column(String, nullable=False, default="")
    stage = Column(Integer, nullable=False, default=0)

    # Relationship back to the deck
    deck = relationship("Deck", back_populates="cards")
