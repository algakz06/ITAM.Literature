import asyncpg
import asyncio

import config
from models import Book, Category

async def make_connection() -> asyncpg.Connection:
    conn = await asyncpg.connect(
        host = config.POSTGRES_HOST,
        user = config.POSTGRES_USER,
        password = config.POSTGRES_PASSWORD,
        database = config.POSTGRES_DB
    )

    return conn

async def get_all_books() -> list[Book]:
    conn = await make_connection()
    books = await conn.fetch('''
        select * from book
    ''')

    return [Book(dict(book)) for book in books]


async def get_categories() -> list:
        conn = await make_connection()
        categories = await conn.fetch('''
            select * from book_category
        ''')

        return [Category(dict(category)) for category in categories]

async def get_book_by_index() -> None:
     pass

async def get_read_books() -> list[Book]: # use for get list of books we read (in past) or reading now
        conn = await make_connection()
        books = await conn.fetch('''
            select * from book where read_start not null
        ''')
    
        return [Book(dict(book)) for book in books]

async def close_connection(conn: asyncpg.Connection) -> None:
    await conn.close()


if __name__ == '__main__':
    async def main():
        print(await get_categories())
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
