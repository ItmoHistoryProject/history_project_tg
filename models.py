from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


# Ассоциативная таблица для категорий
class CategoryEvent(Base):
    __tablename__ = 'category_events'
    category_event_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.event_id'))
    category_id = Column(Integer, ForeignKey('categories.category_id'))

    event = relationship("Event", back_populates="category_links")
    category = relationship("Category", back_populates="event_links")


# Ассоциативная таблица для стран
class CountryEvent(Base):
    __tablename__ = 'country_events'
    country_event_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.event_id'))
    country = Column(String(50), nullable=False)

    event = relationship("Event", back_populates="country_links")


class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True)
    event = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)

    # Связи с категориями
    category_links = relationship("CategoryEvent", back_populates="event")
    categories = association_proxy("category_links", "category")

    # Связи со странами
    country_links = relationship("CountryEvent", back_populates="event")
    countries = association_proxy("country_links", "country")


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, unique=True)

    event_links = relationship("CategoryEvent", back_populates="category")
    events = association_proxy("event_links", "event")