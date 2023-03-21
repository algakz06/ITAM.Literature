from aiogram.dispatcher.filters.state import State, StatesGroup

class Voting(StatesGroup):
    in_vote_mode = State()

class VotingProcess(StatesGroup):
    enter_vote_dates = State()