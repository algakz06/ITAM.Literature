from dataclasses import dataclass
from typing import Optional

@dataclass
class Book:
    id: int
    name: str
    category_id: int
    category_name: str
    author: str
    read_start: str | None
    read_finish: str | None
    read_comments: str | None

    def __init__(self, book_dict: dict):
        self.id = book_dict.get('id')
        self.category_id = book_dict.get('category_id')
        self.category_name = book_dict.get('category_name')
        self.read_start = book_dict.get('read_start')
        self.read_finish = book_dict.get('read_finish')
        self.read_comments = book_dict.get('read_comments')
        try:
            self.name, self.author = tuple(atr.strip() for atr in book_dict.get('name').split('::'))
        except ValueError:
            self.name, self.author = book_dict.get('name'), ''

@dataclass
class Category:
    id: int
    name: str
    books: Optional[list[Book]] = None

    def __init__(self, category_dict: dict[int, str]):
        self.id = category_dict.get('id')
        self.name = category_dict.get('name')

