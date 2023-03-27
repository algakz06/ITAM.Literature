from dataclasses import dataclass
from typing import Optional, Union, List
from datetime import datetime
from itamliterature.models import db_models
from itamliterature import config
from enum import Enum


@dataclass
class Book:
    id: int
    name: str
    category_id: int
    author: str
    read_start: Union[str, None]
    read_finish: Union[str, None]
    read_comments: Union[str, None]

    def is_started(self) -> bool:
        if self.read_start is not None:
            now_date = datetime.now().date()
            start_read_date = datetime.strptime(
                self.read_start, config.DATE_FORMAT
            ).date()

            return start_read_date >= now_date

        return False

    def is_finished(self) -> bool:
        if self.read_finish is not None:
            now_date = datetime.now().date()
            finish_read_date = datetime.strptime(
                self.read_finish, config.DATE_FORMAT
            ).date()

            return finish_read_date <= now_date

        return False

    def is_planned(self) -> bool:
        if self.read_start is not None:
            now_date = datetime.now().date()
            start_read_date = datetime.strptime(
                self.read_start, config.DATE_FORMAT
            ).date()

            return start_read_date >= now_date

        return False

    def __init__(self, book: db_models.Book):
        self.id = book.id
        self.category_id = book.category_id
        self.read_start = book.read_start
        self.read_finish = book.read_finish
        self.read_comments = book.read_comments
        try:
            self.name, self.author = tuple(atr.strip() for atr in book.name.split('::'))
        except ValueError:
            self.name, self.author = book.name, ''

@dataclass
class Category:
    id: int
    name: str
    books: Optional[list[Book]] = None
    leaders: Optional[list[Book]] = None

    def __init__(self, category: db_models.BookCategory):
        self.id = category.id
        self.name = category.name

class Voting(Enum):
    Category = 1
    Book = 2

class Vote():
    first_vote: int
    second_vote: int
    third_vote: int

    def __init__(self, votes: List[int]) -> None:
        self.first_vote, self.second_vote, self.third_vote = votes
        
class VoteResult():
    first_place: int
    second_place: int
    third_place: int
    
    def __init__(self, places: List[int]) -> None:
        self.first_place, self.second_place, self.third_place = places
        
if __name__ == '__main__':
    print(Voting.Category)
        
