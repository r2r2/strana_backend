from typing import Any

import src.users.repos as users_repo


def user_tag_test_wrapper(func):
    """
    Декоратор для автоматического добавления тега 'Тест'
    при отправке в срм в методе создания карточки контактов
    и в методе создания карточки сделок для тестового пользователя.
    """
    async def inner_function(*args, creator_user_id=None, **kwargs):
        if creator_user_id:
            user_repo: users_repo.UserRepo = users_repo.UserRepo()
            filters: dict[str: Any] = dict(id=creator_user_id)
            creator_user: users_repo.User = await user_repo.retrieve(filters=filters)

            if creator_user.is_test_user:
                tags = kwargs.get('tags')
                if tags is None:
                    tags = ["Тест"]
                elif "Тест" not in tags:
                    tags = tags + ["Тест"]
                kwargs['tags'] = tags

        return await func(*args, **kwargs)
    return inner_function
