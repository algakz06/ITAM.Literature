from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, desc
from sqlalchemy.exc import NoResultFound, DataError, IntegrityError

from loguru import logger
from datetime import datetime, date
from typing import Union, Tuple, List, Optional
import random

from itamliterature import config
from itamliterature.models.db_models import (
    Book,
    BookCategory,
    Base,
    Voting,
    VoteCategory,
    VoteBook,
    BotUser,
    VoteResults,
)
from itamliterature.models import models
from itamliterature.utils import schulze, utilities


class DBManager:
    # region inner methods
    def __init__(self):
        self._connect()
        self._recreate_table()
        self.db_session()

    def _connect(self) -> None:
        self.engine = create_engine(
            f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DB}",
            echo=True,
        )

    def _recreate_table(self) -> None:
        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        try:
            with open("itamliterature/db.sql", "r") as file:
                sql = file.read().split("\n")

            queries = [query.strip() for query in sql if query.strip()]

            with self.engine.connect() as connection:
                for query in queries:
                    connection.execute(text(query))
                connection.commit()
                logger.info(".sql file had been loaded successfully")
        except Exception as error:
            logger.error(f".sql file hand't been loaded {error}")

    def db_session(self) -> None:
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def close_connection(self) -> None:
        self.engine.dispose()

    def __del__(self) -> None:
        self.close_connection()

    # endregion

    # region get methods

    # region get categories
    def get_categories(self) -> List[models.Category]:
        categories: List[models.Category] = [
            models.Category(category)
            for category in self.session.query(BookCategory).all()
        ]

        return categories

    def get_all_categories_with_books(self) -> List[models.Category]:
        categories: List[models.Category] = self.get_categories()
        return self.get_categories_with_books(categories)

    def get_books_by_category(self, category: models.Category) -> List[models.Book]:
        return [
            models.Book(book)
            for book in self.session.query(Book)
            .filter(Book.category_id == category.id)
            .all()
        ]

    def get_category_by_index(self, indexes: List[int]) -> List[models.Category]:
        return [
            models.Category(category)
            for category in self.session.query(BookCategory)
            .filter(BookCategory.id.in_(indexes))
            .all()
        ]

    def get_categories_with_books(
        self, categories: List[models.Category]
    ) -> List[models.Category]:
        categories = categories
        for category in categories:
            category.books = [
                models.Book(book)
                for book in self.session.query(Book).filter(
                    Book.category_id == category.id
                )
            ]
        return categories

    def get_results_of_last_category_voting(self) -> List[models.Category]:
        last_voting = self.get_last_voting()
        if last_voting is None:
            return []

        results = self.get_voting_results(last_voting.id)
        return self.get_category_by_index(results)

    # endregion

    # region get books

    def get_books(self) -> List[models.Book]:
        return [models.Book(book) for book in self.session.query(Book).all()]

    def get_book_by_index(self, indexes: List[int]) -> List[Book]:
        return self.session.query(Book).filter(Book.id.in_(indexes)).all()

    def get_now_read_books(self) -> List[models.Book]:
        return [
            models.Book(book)
            for book in self.session.query(Book)
            .filter(Book.read_finish > datetime.now())
            .all()
        ]

    def get_already_read_books(self) -> List[Book]:
        return [
            models.Book(book)
            for book in self.session.query(Book)
            .filter(
                Book.read_start.isnot(None),
                Book.read_finish.isnot(None),
                Book.read_finish < datetime.now(),
            )
            .all()
        ]

    # endregion

    # endregion

    # region voting methods

    def get_current_or_last_voting(self) -> Tuple[str, Voting]:
        if (
            self.session.query(Voting).order_by(desc(Voting.voting_finish)).first()
            is None
        ):
            return ("no_voting", None)
        try:
            return (
                "now",
                self.session.query(Voting)
                .filter(
                    Voting.voting_start.isnot(None),
                    Voting.voting_finish > datetime.now(),
                )
                .one(),
            )
        except NoResultFound:
            return (
                "last",
                self.session.query(Voting).order_by(desc(Voting.voting_finish)).first(),
            )

    def get_voting_results(self, voting_id: int) -> List[int]:
        result = (
            self.session.query(VoteResults)
            .filter(VoteResults.voting_id == voting_id)
            .one()
        )

        return [result.first_place_id, result.second_place_id, result.third_place_id]

    def get_last_voting(self) -> Union[Voting, None]:
        try:
            return (
                self.session.query(Voting)
                .filter(Voting.voting_finish < datetime.now())
                .order_by(Voting.id.desc())
                .first()
            )
        except NoResultFound:
            return None

    def get_category_votes(self, voting_id: int) -> List[models.Vote]:
        return [
            models.Vote(
                [
                    vote.first_category_id,
                    vote.second_category_id,
                    vote.third_category_id,
                ]
            )
            for vote in self.session.query(VoteCategory).filter(
                VoteCategory.voting_id == voting_id
            )
        ]

    def get_book_votes(self, vote_id: int) -> List[models.Vote]:
        return [
            models.Vote([vote.first_book_id, vote.second_book_id, vote.third_book_id])
            for vote in self.session.query(VoteBook).filter(
                VoteBook.voting_id == vote_id
            )
        ]

    def insert_vote(
        self, voting_id: int, user_id: int, voting_type: int, vote: models.Vote
    ) -> bool:
        if voting_type == models.Voting.Category.value:
            vote = VoteCategory(
                voting_id=voting_id,
                user_id=user_id,
                first_category_id=vote.first_vote,
                second_category_id=vote.second_vote,
                third_category_id=vote.third_vote,
            )
        elif voting_type == models.Voting.Book.value:
            vote = VoteBook(
                voting_id=voting_id,
                user_id=user_id,
                first_book_id=vote.first_vote,
                second_book_id=vote.second_vote,
                third_book_id=vote.third_vote,
            )
        try:
            self.session.merge(vote)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            return False

        logger.info(f"vote had been inserted user_id={user_id}, vote={vote}")

        self.update_voting_results(voting_id, voting_type)

        return True

    def update_voting_results(self, voting_id: int, voting_type: int) -> None:
        if voting_type == models.Voting.Category.value:
            votes = self.get_category_votes(voting_id)
            candidates = [category.id for category in self.get_categories()]
        elif voting_type == models.Voting.Book.value:
            votes = self.get_book_votes(voting_id)
            candidates = [category.id for category in self.get_books()]

        weighted_ranks = utilities.data_for_shulze(votes)

        leaders = schulze.compute_ranks(candidates, weighted_ranks)
        try:
            leaders = models.VoteResult(
                [random.choice(leader) for leader in leaders[:3]]
            )
        except ValueError:
            return

        result = VoteResults(
            voting_id=voting_id,
            voting_type=voting_type,
            first_place_id=leaders.first_place,
            second_place_id=leaders.second_place,
            third_place_id=leaders.third_place,
        )

        self.session.merge(result)
        self.session.commit()

    # endregion

    # region admin methods

    def start_voting(self, start: str, finish: Optional[str] = None) -> bool:
        format_date = lambda date: datetime.strptime(date, "%d.%m.%Y").strftime(
            "%Y-%m-%d"
        )
        status, voting = self.get_current_or_last_voting()

        if status == "no_voting":
            self.session.add(
                Voting(
                    voting_start=format_date(start),
                    voting_finish=format_date(finish),
                    voting_type=models.Voting.Category.value,
                )
            )
            logger.info(f"voting had been started; start={start}, finish={finish}")
            return True

        if voting.voting_finish > datetime.strptime(start, "%d.%m.%Y").date():
            logger.error(f"voting hadnt been started error=wrong date")
            return False

        if status == "last":
            try:
                match voting.voting_type:
                    case models.Voting.Category.value:
                        self.session.add(
                            Voting(
                                voting_start=format_date(start),
                                voting_finish=format_date(finish),
                                voting_type=models.Voting.Book.value,
                            )
                        )
                    case models.Voting.Book.value:
                        self.session.add(
                            Voting(
                                voting_start=format_date(start),
                                voting_finish=format_date(finish),
                                voting_type=models.Voting.Category.value,
                            )
                        )
                logger.info(f"voting had been started; start={start}, finish={finish}")
            except DataError as error:
                logger.error(f"voting hadnt been started error={error}")
                return False

        self.session.commit()
        return True

    def end_voting(self) -> bool:
        status, voting = self.get_current_or_last_voting()
        if status == "now":
            voting.voting_finish = datetime.now()
            self.session.merge(voting)
            self.session.commit()
            logger.info(f"voting had been ended")
            return True
        else:
            logger.info(f"{voting} voting hadnt been ended")
            return False

    # endregion

    # region general methods

    def insert_bot_user(self, user_id: int) -> None:
        self.session.merge(BotUser(telegram_id=user_id))
        self.session.commit()

        logger.info(f"bot_user had been inserted {user_id}")

    def is_admin(self, id: int) -> bool:
        try:
            self.session.query(BotUser).filter(
                BotUser.telegram_id == id, BotUser.is_admin == True
            ).one()
            return True
        except NoResultFound:
            return False

    # endregion

    # region adding methods

    def add_category(self, name: str) -> bool:
        self.session.merge(BookCategory(name=name))
        self.session.commit()

        logger.info(f"category had been added {name}")

        return True

    def add_book(self, name: str, category: int) -> bool:
        self.session.merge(Book(name=name, category_id=category))
        self.session.commit()

        logger.info(f"book had been added {name}")

        return True

    def add_admin(self, id: int) -> bool:
        self.session.merge(BotUser(telegram_id=id, is_admin=True))
        self.session.commit()

        logger.info(f"admin had been added {id}")

        return True

    # endregion


if __name__ == "__main__":
    db = DBManager()
    logger.info(db.get_current_voting())
