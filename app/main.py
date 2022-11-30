from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from .api import OkBot, accounts, events
from .core.config import engine, get_db
from sqlalchemy.orm import Session
from .db import models
from .db.schemas import BotSchema, ActionSchema, ActionSchemaBase, ActionSchemaComment, DefaultResponse, Responses
from typing import List
import os
import random

PATH_TO_SRC = os.path.abspath('src')
PATH_TO_LOGS = os.path.abspath('logs')

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory='./app/templates')
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
async def on_startup():
    active_all_accounts()


@app.get('/get_accounts')
async def get_accounts():
    _accounts = accounts.get_all_accounts()
    return _accounts


@app.post('/create-bots', response_model=Responses)
async def create_bots(new_bots: List[BotSchema], db: Session = Depends(get_db)):
    """
    Функция добавления аккаунтов
    """
    results = []
    
    for _bot in new_bots:
        try:
            _new_account = accounts.create_new_account(_bot.login, _bot.password, db)
        except:
            results.append(
                DefaultResponse(
                    login=_bot.login,
                    status='Ошибка',
                    msg='Аккаунт существует'
                )
            )
            continue
        
        _bot_driver = OkBot.Bot(_new_account.login, _new_account.password)
        
        if _bot_driver.is_auth:
            dict_bots[_new_account.id] = _bot_driver
            results.append(
                DefaultResponse(
                    login=_bot.login,
                    status='Успешно',
                    msg='Аккаунт добавлен'
                )
            )
        else:
            results.append(
                DefaultResponse(
                    login=_new_account.login,
                    status='Ошибка',
                    msg='Неверно введены данные от аккаунта'
                )
            )
            accounts.delete_account_by_id(db, _new_account.id)
    
    return Responses(results=results)


@app.post('/like-posts', response_model=Responses)
async def like_posts(actions: List[ActionSchema], db: Session = Depends(get_db)):
    """
    Функция для лайков под посты
    """
    results = []
    
    if dict_bots:
        for action in actions:
            if action.target_id is None:
                results.append(DefaultResponse(
                    login=action.login,
                    status='Ошибка',
                    msg='Id пользователя не введен',
                ))
                continue
            
            for id, driver in dict_bots.items():
                events.create_log(str(id), 'like posts', db)
                driver.like_users(action.target_id)
                
                results.append(DefaultResponse(
                    login=action.login,
                    status='Успешно',
                    msg='Лайки проставлены',
                ))
            
        return Responses(results=results)
    else:
        results.append(
            DefaultResponse(
                status='Ошибка',
                msg='Нет аккаунтов',
            )
        )
        return Responses(results=results)


@app.post('/comment-posts', response_model=Responses)
async def comment_posts(actions: List[ActionSchemaComment], db: Session = Depends(get_db)):
    """
    Создание коментариев под посты пользователя
    """
    results = []
    
    if dict_bots:
        for action in actions:
            if (action.target_id is None) or (action.comment is None):
                results.append(DefaultResponse(
                    login=action.login,
                    status='Ошибка',
                    msg='Не все данные заполнены',
                ))
                continue
            
                        
            for id, driver in dict_bots.items():
                events.create_log(str(id), 'comment post', db)
                # image_bytes = driver.create_comment_in_user_profile(action.target_id, action.comment)
                driver.create_comment_in_user_profile(action.target_id, action.comment)
                # for idx, image in enumerate(image_bytes):
                #     random_name = random.randint(0, 10000)
                #     file = open(f'.{PATH_TO_SRC}/{id}_{random_name}_comment.png', 'wb')
                #     file.write(image)
                #     file.close()
                #
                # screenshots = await create_urls_for_image(id)
                
                results.append(DefaultResponse(
                    status='Успешно',
                    msg='Комментарии написаны',
                ))
            
                
        return Responses(results=results)
    else:
        results.append(
            DefaultResponse(
                status='Ошибка',
                msg='Нет аккаунтов',
            )
        )
        return Responses(results=results)
    
    
async def create_urls_for_image(id: str):
    urls = []

    pattern = f'{id}_'
    for root, dirs, files in os.walk('.'+PATH_TO_SRC):
            with open(f'.{PATH_TO_LOGS}/{id}_screenshots.txt', 'w+', encoding='utf-8') as image:
                for file in files:
                    if pattern == file[:2]:
                        image.write(f'http://localhost:8000/get_screenshot/{file}\n')
                        urls.append(f'http://localhost:8000/get_screenshot/{file}')
            image.close()
    return urls

@app.post('/create-posts', response_model=DefaultResponse)
async def create_posts(actions: List[ActionSchemaComment], db: Session = Depends(get_db)):
    """
    Создания постов в профиле
    """
    results = []
    
    if dict_bots:
        for action in actions:
            if action.comment is None:
                results.append(DefaultResponse(
                    login=action.login,
                    status='Ошибка',
                    msg='Комментарий пуст',
                ))
                continue
            
            
            for id, driver in dict_bots.items():
                events.create_log(str(id), 'create post', db)
                image_bytes = driver.create_post(action.comment)
                
                with open(f'./app/src/image_{id}_create_post.png', 'wb') as image:
                    image.write(image_bytes)
                
                screenshots = await create_urls_for_image()    
                    
                results.append(DefaultResponse(
                    login=action.login,
                    status='Успешно',
                    msg='Пость создан',
                ))
            
            
        return Responses(results=results)
    else:
        results.append(
            DefaultResponse(
                status='Ошибка',
                msg='Нет аккаунтов',
            )
        )
        return Responses(results=results)
    
    
@app.post('/delete-accounts', response_model=Responses)
async def delete_accounts(actions: List[ActionSchemaBase], db: Session = Depends(get_db)):
    results = []
    existing_accounts = []
    
    if dict_bots:
        for action in actions:
            if action.login is None:
                results.append(
                    DefaultResponse(
                        status='Ошибка',
                        msg='Логин от аккаунта не введен',
                    )
                )
                continue
            
            existing_accounts.append(accounts.get_account_by_login(db, action.login))
        
        for account in existing_accounts:
            results.append(DefaultResponse(
                    login=action.login,
                    status='Успешно',
                    msg='Аккаунт удалён',
                ))
            accounts.delete_account_by_id(db, account.id)
            
        return Responses(results=results)
    else:
        results.append(
            DefaultResponse(
                status='Ошибка',
                msg='Нет аккаунтов',
            )
        )
        return Responses(results=results)


@app.get('/get_screenshot/{bot_login}', response_class=FileResponse)
async def get_screenshot(bot_login: str, db: Session = Depends(get_db)):
    bot_id = accounts.get_account_by_login(db, bot_login).id

    if dict_bots[bot_id]:
        img_bytes = dict_bots[bot_id].driver.get_screenshot_as_png()
        file_name = f'{bot_id}_{random.randint(0, 100000)}.png'
        with open(f'.{PATH_TO_SRC}/{file_name}', 'wb') as image:
            image.write(img_bytes)
        image.close()
    return FileResponse(f'.{PATH_TO_SRC}/{file_name}')


# @app.get('/get_logs/{bot_login}', response_class=FileResponse)
# async def get_logs(bot_login: str, db: Session = Depends(get_db)):
#     bot_id = accounts.get_account_by_login(db, bot_login).id
#     return FileResponse(f'./app/logs/{bot_id}_screenshots.txt')
#
#
# @app.get('/detail_screenshot/{file_name}', response_class=FileResponse)
# async def detail_screenshot(file_name: str):
#     return FileResponse(f'.{PATH_TO_SRC}/{file_name}')