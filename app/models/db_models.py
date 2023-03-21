from sqlalchemy import Column, ForeignKey, Integer, String,\
     Text, DateTime, UniqueConstraint, CheckConstraint,\
     ForeignKeyConstraint, Date, Identity, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List

Base = declarative_base()

class BotUser(Base):
    __tablename__ = 'bot_user'

    telegram_id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class BookCategory(Base):
    __tablename__ = 'book_category'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    name = Column(String(60), nullable=False, unique=True)
    ordering = Column(Integer, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f'<BookCategory(id={self.id}, name={self.name})>'

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    name = Column(Text)
    category_id = Column(Integer, ForeignKey('book_category.id'))
    ordering = Column(Integer, nullable=False)
    read_start = Column(Date)
    read_finish = Column(Date)
    read_comments = Column(Text)
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['book_category.id']),
        CheckConstraint(
            (
                (read_finish > read_start)
                & (read_finish != None)
                & (read_start != None)
            ) | (
                (read_finish == None) | (read_start == None)
            )
        ),
        UniqueConstraint('category_id', 'ordering')
    )

    def __repr__(self) -> str:
        return f'<Book(id={self.id}, name={self.name}, category_id={self.category_id})>'



class VoteType(Base):
    __tablename__ = 'vote_type'

    id = Column(Integer, primary_key=True)
    vote_type_name = Column(String, nullable=True)


class Voting(Base):
    __tablename__ = 'voting'

    id = Column(Integer, primary_key=True)
    voting_start = Column(Date, nullable=False, unique=True)
    voting_finish = Column(Date, nullable=True, unique=True)
    voting_type = Column(Integer, ForeignKey('vote_type.id'), nullable=False)
    __table_args__ = (
        CheckConstraint(voting_finish > voting_start),
    )


class VoteBook(Base):
    __tablename__ = 'vote_book'

    vote_id = Column(Integer, ForeignKey('voting.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('bot_user.telegram_id'), primary_key=True)
    first_book_id = Column(Integer, ForeignKey('book.id'))
    second_book_id = Column(Integer, ForeignKey('book.id'))
    third_book_id = Column(Integer, ForeignKey('book.id'))
    __table_args__ = (
        ForeignKeyConstraint(['vote_id'], ['voting.id']),
        ForeignKeyConstraint(['user_id'], ['bot_user.telegram_id']),
    )


class VoteCategory(Base):
    __tablename__ = 'vote_category'

    vote_id = Column(Integer, ForeignKey('voting.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('bot_user.telegram_id'), primary_key=True)
    first_category_id = Column(Integer, ForeignKey('book_category.id'))
    second_category_id = Column(Integer, ForeignKey('book_category.id'))
    third_category_id = Column(Integer, ForeignKey('book_category.id'))
    __table_args__ = (
        ForeignKeyConstraint(['vote_id'], ['voting.id']),
        ForeignKeyConstraint(['user_id'], ['bot_user.telegram_id']),
    )
