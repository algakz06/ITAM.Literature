from loguru import logger
from datetime import datetime
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from itamliterature import config
from itamliterature.keyboards import inline_keyboards
from itamliterature.db import DBManager
from itamliterature.templates import render_template
from itamliterature.models.models import Voting, Vote
from itamliterature.models import states
from itamliterature.utils import schulze, utilities


# filters
admin_only = lambda message: db.is_admin(message.from_user.id)
# Initialize bot and dispatcher
bot = Bot(token=config.TELEGRAM_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

db = DBManager()

#default users handlers
@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    db.add_user(message.from_user.id)
    await message.answer(render_template('start.j2'))

#-------------------------------------------------------------------------
@dp.message_handler(commands=['allbooks'])
async def all_books(message: types.Message) -> None:
    categories_with_books = db.get_all_categories_with_books()
    keyboard = inline_keyboards.get_categories_keyboard(0, len(categories_with_books), config.VOTE_BOOKS_CALLBACK_PATTERN)
    await message.answer(render_template('category_with_books.j2', {
        'category': categories_with_books[0],
        'voting': False
    }), reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith(config.VOTE_BOOKS_CALLBACK_PATTERN))
async def all_books_change_page(call: types.CallbackQuery):
    categories_with_books = db.get_all_categories_with_books()
    index = int(call.data.split(config.VOTE_BOOKS_CALLBACK_PATTERN)[1])
    keyboard = inline_keyboards.get_categories_keyboard(index, len(categories_with_books), config.VOTE_BOOKS_CALLBACK_PATTERN)
    await call.message.edit_text(render_template('category_with_books.j2', {
            'category': categories_with_books[index],
            'voting': False
        }
    ), reply_markup=keyboard)

#-------------------------------------------------------------------------
@dp.message_handler(commands=['allcategories'])
async def all_categories(message: types.Message) -> None:
    categories = db.get_categories()

    await message.answer(
        render_template('categories.j2', {
        'categories': categories,
        })
    )

#-------------------------------------------------------------------------
@dp.message_handler(commands='now')
async def now_books(message: types.Message) -> None:
    now_read_books = db.get_now_read_books()

    await message.answer(
        render_template('now.j2', {
        'now_read_books': now_read_books,
        'date_now': datetime.now()
        })
    )

#-------------------------------------------------------------------------
@dp.message_handler(commands='already')
async def already_books(message: types.Message) -> None:
    already_read_books = db.get_already_read_books()

    await message.answer(
        render_template('already.j2', {
        'now_read_books': already_read_books
        })
    )

# VOTING BLOCK
#-------------------------------------------------------------------------
@dp.message_handler(commands=['vote'])
async def vote(message: types.Message) -> None:
    user = await bot.get_chat_member(chat_id='-1001536842419', user_id=message.from_user.id)

    if user.status == 'left':
        await message.answer(render_template('vote_cant_vote.j2'))
        return None

    status, voting = db.get_current_or_last_voting()

    if status != 'now':
        await message.answer(render_template('vote_no_actual_voting.j2'))
        return None
    
    if voting.voting_type == Voting.Category.value:
        categories = db.get_categories()

        await states.Voting.in_vote_mode.set()

        await message.answer(render_template('categories.j2', {
            'categories': categories,
            'voting': True
        }))

    elif voting.voting_type == Voting.Book.value:
        pass

#-------------------------------------------------------------------------
@dp.message_handler(state=states.Voting.in_vote_mode)
async def insert_votes(message: types.Message, state: FSMContext):
    votes = [int(vote) for vote in re.findall('[0-9]+', message.text)]

    if len(votes) != 3:
        message.answer(render_template('vote_incorrect_input.j2'))

    _, voting = db.get_current_or_last_voting()

    if voting.voting_type == Voting.Category.value:
        insert_result = db.insert_vote_category(voting.id, message.from_user.id, Vote(votes))

        if insert_result == True:
            categories = db.get_category_by_index(votes)
            await message.answer(render_template('vote_success.j2', {
                'selected_values': categories
            }))
            await state.finish()
        else:
            await message.answer('vote_incorrect_categories.j2')
    elif voting.vote_typing == Voting.Book.value:
        insert_result = db.insert_vote_book(voting.id, message.from_user.id, Vote(votes))

        if insert_result == True:
            books = db.get_book_by_index(votes)
            await message.answer(render_template('vote_success.j2', {
                'selected_values': books
            }))
            await state.finish()
        else:
            await message.answer('vote_incorrect_books.j2')


#-------------------------------------------------------------------------
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

# VOTING BLOCK ENDED
#-------------------------------------------------------------------------
@dp.message_handler(admin_only, commands='start_voting')
async def start_voting(message: types.Message, state: FSMContext):
    await message.answer(render_template('start_voting_enter_dates.j2'))
    await state.set_state(states.VotingProcess.enter_vote_dates)
    
@dp.message_handler(state=states.VotingProcess.enter_vote_dates)
async def insert_voting_dates(message: types.Message, state: FSMContext):
    start_date, finish_date = message.text.split('-')
    db.start_voting(start_date, finish_date)
    await message.answer('Успешно')
    await state.finish()
    
#-------------------------------------------------------------------------
@dp.message_handler(commands='voteresults')
async def get_vote_results(message: types.Message) -> None:
    status, voting = db.get_current_or_last_voting()
    
    votes: list[Vote]
    candidates: list[int]
    
    if voting.voting_type == Voting.Category.value:
        votes = db.get_category_votes(voting.id)
        candidates = [category.id for category in db.get_categories()]
    elif voting.voting_type == Voting.Book.value:
        votes = db.get_book_votes(voting.id)
        
    if not votes:
        await message.answer(render_template('vote_results_no_data.j2'))
        return
    
    weighted_ranks = utilities.data_for_shulze(votes)
    
    leaders = schulze.compute_ranks(candidates, weighted_ranks)
    
    leaders = [db.get_category_by_index(index) for index in leaders[:10]]
    
    
    await message.answer(render_template('vote_results.j2', {
        'status': status,
        'leaders': leaders,
        'voting': voting
    }))
    
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)