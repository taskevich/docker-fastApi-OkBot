import os

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import Generator

from api import OkBot, accounts, events
from core.config import engine, get_db
from db import models
from db.schemas import BotSchema, ActionSchema, ActionSchemaBase, ActionSchemaComment, DefaultResponse


PATH_TO_SRC = os.path.abspath('src')

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
dict_bots = {}


def active_all_accounts():
    """
    Функция авторизации во все аккаунты
    """
    _accounts = accounts.get_all_accounts()
    if _accounts:
        for _account in _accounts:
            _bot_driver = OkBot.Bot(_account.login, _account.password)
            dict_bots[_account.id] = _bot_driver


@app.on_event('startup')
def on_startup():
    active_all_accounts()


@app.get('/get_accounts')
def get_accounts():
    _accounts = accounts.get_all_accounts()
    return _accounts


@app.post('/create-bot', response_model=DefaultResponse)
def create_bot(_bot: BotSchema, db: Session = Depends(get_db)):
    """
    Функция добавления аккаунтов
    """
    try:
        _new_account = accounts.create_new_account(_bot.login, _bot.password, db)
    except:
        return DefaultResponse(
            status='Ошибка',
            msg='Аккаунт существует'
        )

    _bot_driver = OkBot.Bot(_new_account.login, _new_account.password)

    if _bot_driver.is_auth:
        dict_bots[_new_account.id] = _bot_driver
        return DefaultResponse(
            status='Успешно',
            msg='Аккаунт добавлен'
        )
    else:
        accounts.delete_account_by_id(db, _new_account.id)
        return DefaultResponse(
            status='Ошибка',
            msg='Неверно введены данные от аккаунта'
        )


@app.post('/like-posts', response_model=DefaultResponse)
def like_posts(action: ActionSchema, db: Session = Depends(get_db)):
    """
    Функция для лайков под посты
    """
    if dict_bots:
        if action.target_id is None:
            return DefaultResponse(
                status='Ошибка',
                msg='Id пользователя не введен',
            )

        for id, driver in dict_bots.items():
            events.create_log(str(id), 'like posts', db)
            driver.like_users(action.target_id)

        return DefaultResponse(
            status='Успешно',
            msg='Лайки проставлены',
        )
    else:
        return DefaultResponse(
            status='Ошибка',
            msg='Нет аккаунтов',
        )


@app.post('/comment-posts', response_model=DefaultResponse)
def comment_posts(action: ActionSchemaComment, db: Session = Depends(get_db)):
    """
    Создание коментариев под посты пользователя
    """
    if dict_bots:
        if (action.target_id is None) or (action.comment is None):
            return DefaultResponse(
                status='Ошибка',
                msg='Не все данные заполнены',
            )

        for id, driver in dict_bots.items():
            events.create_log(str(id), 'comment post', db)
            driver.create_comment_in_user_profile(action.target_id, action.comment)

        return DefaultResponse(
            status='Успешно',
            msg='Комментарии написаны',
        )
    else:
        return DefaultResponse(
            status='Ошибка',
            msg='Нет аккаунтов',
        )


async def create_urls_for_image(id: str):
    urls = []

    pattern = f'{id}_'
    for root, dirs, files in os.walk('.' + PATH_TO_SRC):
        with open(f'.{PATH_TO_SRC}/{id}_screenshots.txt', 'w+', encoding='utf-8') as image:
            for file in files:
                if pattern == file[:2]:
                    image.write(f'http://localhost:8000/get_screenshot/{file}\n')
                    urls.append(f'http://localhost:8000/get_screenshot/{file}')
        image.close()
    return urls


@app.post('/create-posts', response_model=DefaultResponse)
def create_posts(action: ActionSchemaComment, db: Session = Depends(get_db)):
    """
    Создания постов в профиле
    """
    if dict_bots:
        if action.comment is None:
            return DefaultResponse(
                status='Ошибка',
                msg='Комментарий пуст',
            )

        for id, driver in dict_bots.items():
            events.create_log(str(id), 'create post', db)
            driver.create_post(action.comment)

        return DefaultResponse(
            status='Успешно',
            msg='Пость создан',
        )
    else:
        return DefaultResponse(
            status='Ошибка',
            msg='Нет аккаунтов',
        )


@app.post('/delete-account', response_model=DefaultResponse)
async def delete_account(action: ActionSchemaBase, db: Session = Depends(get_db)):
    if dict_bots:
        if action.login is None:
            return DefaultResponse(
                status='Ошибка',
                msg='Логин от аккаунта не введен',
            )

        accounts.delete_account_by_id(db, action.id)

        return DefaultResponse(
            status='Успешно',
            msg='Аккаунт удалён',
        )
    else:
        return DefaultResponse(
            status='Ошибка',
            msg='Нет аккаунтов',
        )


@app.get('/get_screenshot/{bot_login}')
def get_screenshot(bot_login: str, db: Session = Depends(get_db)):
    bot_id = accounts.get_account_by_login(db, bot_login).id

    if not os.path.exists(f'.{PATH_TO_SRC}'):
        os.mkdir('.' + PATH_TO_SRC)

    if dict_bots[bot_id]:
        img_bytes = dict_bots[bot_id].driver.get_screenshot_as_png()
    return Response(content=img_bytes, media_type='image/png')


def gen(bot_id: int) -> Generator:
    while True:
        frame = dict_bots[bot_id].driver.get_screenshot_as_png()
        yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')


@app.get('/live_screenshot/{bot_login}')
def live_screen(bot_login: str, db: Session = Depends(get_db)):
    bot_id = accounts.get_account_by_login(db, bot_login).id
    if dict_bots[bot_id]:
        return StreamingResponse(gen(bot_id), media_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return DefaultResponse(
            status='Ошибка',
            msg='Нет аккаунта, либо он не активен.',
        )
