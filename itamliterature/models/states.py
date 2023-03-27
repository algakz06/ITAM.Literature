from aiogram.dispatcher.filters.state import State, StatesGroup

class Voting(StatesGroup):
    in_vote_mode = State()

class VotingProcess(StatesGroup):
    enter_vote_dates = State()
    
class CategoryProcess(StatesGroup):
    add_category = State()
    
class BookProcess(StatesGroup):
    add_book = State()
    
class AdminProcess(StatesGroup):
    add_admin = State()