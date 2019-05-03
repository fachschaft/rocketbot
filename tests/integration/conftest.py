import asyncio
from typing import Iterable, List

import pytest
from rocketchat_API.rocketchat import RocketChat as RestClient

import rocketbot.master as master
import rocketbot.models as m

from ..utils import random_string

_admin_user = None


def pytest_sessionstart(session: pytest.Session) -> None:
    """This function is executed before any integration test is run.

    The admin is created her because the first user is by default admin
    """

    global _admin_user

    result = RestClient().users_register(
        username='admin',
        name='Administrator',
        email='admin@example.com',
        password='admin').json()
    if result['success']:
        _admin_user = m.create(m.User, result['user'])
    else:
        restClient = RestClient(user='admin', password='admin')
        result = restClient.users_info(username='admin').json()
        _admin_user = m.create(m.User, result['user'])


@pytest.yield_fixture
def event_loop() -> Iterable[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for each test case.
    Fixes: https://github.com/pytest-dev/pytest-asyncio/issues/29
    """
    policy = asyncio.get_event_loop_policy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    _close = res.close
    # Ignore mypy bug/limitation -> https://github.com/python/mypy/issues/2427
    res.close = lambda: None  # type: ignore

    yield res

    _close()


@pytest.fixture
def admin_user() -> m.User:
    if _admin_user is None:
        raise Exception("Admin user is not set up correctly")
    return _admin_user


@pytest.fixture
def admin(admin_user: m.User, event_loop: asyncio.AbstractEventLoop) -> master.Master:
    return master.Master('http://localhost:3000', admin_user.username, admin_user.username, tls=False, loop=event_loop)


@pytest.fixture
def bot_user(admin: master.Master) -> m.User:
    return _get_or_create_user(admin, 'bot', 'saBOTeur', roles=['bot'])


@pytest.fixture
def bot(bot_user: m.User, event_loop: asyncio.AbstractEventLoop) -> master.Master:
    return master.Master('http://localhost:3000', bot_user.username, bot_user.username, tls=False, loop=event_loop)


@pytest.fixture
def user_user(admin: master.Master) -> m.User:
    return _get_or_create_user(admin, 'user', 'FirstUser')


@pytest.fixture
def user(user_user: m.User, event_loop: asyncio.AbstractEventLoop) -> master.Master:
    return master.Master('http://localhost:3000', user_user.username, user_user.username, tls=False, loop=event_loop)


@pytest.fixture
def public_channel(admin: master.Master) -> m.Room:
    json = admin.rest_api.channels_create(random_string(10)).json()
    return m.create(m.Room, json['channel'])


def _get_or_create_user(
        master: master.Master,
        username: str,
        displayname: str,
        *,
        roles: List[str] = ['user']) -> m.User:

    result = master.rest_api.users_info(username=username).json()
    if not result['success']:
        result = master.rest_api.users_create(
            username=username,
            name=displayname,
            email=f'{username}@example.com',
            password=username,
            roles=roles
        ).json()

    return m.create(m.User, result['user'])
