from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, desc
from sqlalchemy.exc import NoResultFound, DataError

import pprint
from datetime import datetime
from typing import List

import config
from models.db_models import Book, BookCategory, Base, Voting,\
    VoteCategory, VoteBook, BotUser
from models import models

class DBManager:
    def __init__(self):
        self._connect()
        self._recreate_table()
        self.db_session()

    def _connect(self) -> None:
        self.engine = create_engine(
            f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DB}',
            echo=True
        )

    def _recreate_table(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        with open('app/db.sql', 'r') as file:
            sql = file.read().split('\n')

        queries = [query.strip() for query in sql if query.strip()]

        with self.engine.connect() as connection:
            for query in queries:
                connection.execute(text(query))
            connection.commit()

    def db_session(self) -> None:
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def get_categories(self) -> list[models.Category]:
        categories: list[models.Category] = [models.Category(category)
                                            for category in self.session.query(BookCategory).all()]

        return categories

    def get_all_categories_with_books(self) -> list[models.Category]:
        categories: list[models.Category] = self.get_categories()

        for category in categories:
            category.books = [models.Book(book)
                             for book in self.session.query(Book).filter(
                                Book.category_id == category.id
                            )]

        return categories

    def get_book_by_index(self, indexes: list[int]) -> Book:
        return self.session.query(Book).filter(Book.id.in_(indexes)).all()
    
    def get_category_by_index(self, indexes: list[int]) -> BookCategory:
        return self.session.query(BookCategory).filter(BookCategory.id.in_(indexes)).all()
    
    def get_now_read_books(self) -> list[models.Book]:
        return [
            models.Book(book) for book in self.session.query(Book).filter(
            Book.read_finish > datetime.now()
            ).all()
            ]

    def get_already_read_books(self) -> list[Book]:
        return [
            models.Book(book) for book in self.session.query(Book).filter(
            Book.read_start.isnot(None),
            Book.read_finish.isnot(None),
            Book.read_finish < datetime.now()
            ).all()
            ]
    
    def get_current_voting(self) -> Voting:
        try:
            return self.session.query(Voting).filter(
                Voting.voting_start.isnot(None),
                Voting.voting_finish > datetime.now()
            ).one()
        except NoResultFound:
            return False
        
    def insert_vote_category(self, vote_id: int, user_id: int, vote: models.Vote) -> bool:
        votes = [VoteCategory(vote_id=vote_id,
                              user_id=user_id,
                              first_category_id=vote.first_vote,
                              second_category_id=vote.second_vote,
                              third_category_id=vote.third_vote
                              )]
        try:
            self.session.add_all(votes)
            self.session.commit()
            return True
        except Exception as error:
            print(error)
            return False
        
    def insert_vote_book(self, vote_id: int, user_id: int, vote: models.Vote) -> bool:
        votes = [VoteCategory(vote_id=vote_id,
                              user_id=user_id,
                              first_book_id=vote.first_vote,
                              second_book_id=vote.second_vote,
                              third_book_id=vote.third_vote
                              )]
        try:
            self.session.add_all(votes)
            self.session.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def insert_bot_user(self, user_id: int) -> None:
        self.session.add(BotUser(telegram_id=user_id))
        self.session.commit()
        
    def get_last_voting(self) -> Voting | None:
        try:
            return self.session.query(Voting).order_by(Voting.id.desc()).first()
        except NoResultFound:
            return None

    def start_voting(self, start: str, finish: str | None = None):
        print('hello')
        format_date = lambda date: datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        last_voting: Voting | None = self.get_last_voting()
        
        if last_voting:
            try:
                match last_voting.vote_type:
                    case models.Vote.Category.value:
                        self.session.add(Voting(
                            voting_start=format_date(start),
                            voting_finish=format_date(finish),
                            voting_type=models.Voting.Book.value
                        ))
                    case models.Vote.Book.value:
                        self.session.add(Voting(
                            voting_start=format_date(start),
                            voting_finish=format_date(finish),
                            voting_type=models.Voting.Category.value
                        ))
                return True
            except DataError as error:
                return False
        else:
            self.session.add(Voting(
                            voting_start=format_date(start),
                            voting_finish=format_date(finish),
                            voting_type=models.Voting.Category.value
                        ))
        self.session.commit()

    def is_admin(self, id: int) -> bool:
        try:
            self.session.query(BotUser).filter(BotUser.telegram_id == id).one()
            return True
        except NoResultFound:
            return False


    def close_connection(self) -> None:
        self.engine.dispose()

if __name__ == '__main__':
    db = DBManager()
    pprint.pprint(db.get_current_voting())