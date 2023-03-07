import psycopg2
from psycopg2 import extras

import config
from models import Book, Category

class DB:
    conn: psycopg2._psycopg.connection
    cur: psycopg2._psycopg.cursor

    def __init__(self):
        self.conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            database=config.POSTGRES_DB
        )
        self.cur = self.conn.cursor(cursor_factory=extras.DictCursor)

    def get_all_books(self) -> list[Book]:
        self.cur.execute('''
            select * from book
        ''')

        books = self.cur.fetchall()

        return [Book(dict(book)) for book in books]

    def get_categories(self) -> list:
        self.cur.execute('''
            select * from book_category
        ''')

        categories = self.cur.fetchall()

        return [Category(dict(category)) for category in categories]

    def get_book_by_index(self, index: int) -> Book:
        self.cur.execute('''
            select * from book where id = %s
        ''', [index])

        book = self.cur.fetchone()

        return Book(dict(book))

    def get_read_books(self) -> list[Book]: # use for get list of books we read (in past) or reading now
        self.cur.execute('''
            select * from book where read_start not null and read_finish not null
        ''')

        books = self.cur.fetchall()

        return [Book(dict(book)) for book in books]

    def close_connection(self) -> None:
        self.conn.close()

if __name__ == '__main__':
    db = DB()
    print(db.get_book_by_index(1))

