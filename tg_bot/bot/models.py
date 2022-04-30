from unittest.mock import DEFAULT
from xmlrpc.client import Boolean
import redis
from conf import REDIS_URL, DEFAULT_TIMEDELTA


R = redis.from_url(REDIS_URL)


def set_state(key, value) -> bool:
    return R.set(key=key, value=value)


def set_exp_state(key, value, exp=None) -> bool:
    exp = exp if exp else DEFAULT_TIMEDELTA
    return R.setex(key=key, time=exp, value=value)


def get_state(key) -> str:
    return R.get(key=key)


def is_state_exsists(key) -> bool:
    return R.exists(key=key)


def pop_state(key) -> int:
    return R.delete(key=key)
