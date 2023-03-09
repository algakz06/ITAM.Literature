from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import config
from models.db_models import Book, BookCategory, Base

class DBManager:
    def __init__(self):
        self.engine = create_engine(
            f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DB}',
            echo=True
        )

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        with open('db.sql', 'r') as file:
            sql = file.read().split('\n')

        queries = [query.strip() for query in sql if query.strip()]

        with self.engine.connect() as connection:
            for query in queries:
                connection.execute(text(query))
                connection.commit()

        self.Session = sessionmaker(bind=self.engine)

    def get_all_books(self) -> list[Book]:
        session = self.Session()
        books = session.query(Book, BookCategory.name).join(BookCategory).all()
        return books

    def get_categories(self) -> list:
        session = self.Session()
        categories = session.query(BookCategory).all()
        return categories

    def get_book_by_index(self, index: int) -> Book:
        session = self.Session()
        book = session.query(Book).filter_by(id=index)
        return book

    def get_read_books(self) -> list[Book]:
        session = self.Session()
        books = session.query(Book).filter(Book.read_start.isnot(None), Book.read_finish.isnot(None)).all()
        return books

    def close_connection(self) -> None:
        self.engine.dispose()

if __name__ == '__main__':
    db = DBManager()
    print([book.Book.name for book in db.get_all_books()])