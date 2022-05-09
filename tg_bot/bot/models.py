from unittest.mock import DEFAULT
import redis
from settings import REDIS_URL, DEFAULT_TIMEDELTA


R = redis.from_url(REDIS_URL)


def set_state(key, value) -> bool:
    return R.set(name=key, value=value)


def set_exp_state(key, value, exp=None) -> bool:
    exp = exp if exp else DEFAULT_TIMEDELTA
    return R.setex(name=key, time=exp, value=value)


def get_state(key) -> str:
    return R.get(name=key).decode("utf-8") 


def is_state_exsists(key) -> bool:
    return bool(R.exists(key))


def pop_state(key) -> int:
    return R.delete(name=key)
