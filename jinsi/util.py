from __future__ import annotations

import decimal
import functools
import hashlib
import re
import struct
from decimal import Decimal
from typing import Callable, List, Optional, Union, Dict

import dezimal
from dezimal import Dezimal

from jinsi.exceptions import NoMergePossible


def hash_complex(
        value, *, algo="sha256",
        _prefix: Optional[bytes] = None,
        _none=bytes([3]),
        _true=bytes([5]),
        _false=bytes([7]),
        _zero=bytes([11]),
        _int_neg=bytes([13]),
        _int_pos=bytes([17]),
        _double=bytes([19]),
        _string=bytes([23]),
        _seq=bytes([29]),
        _map=bytes([31]),
        _set=bytes([37]),
        _arbitrary=bytes([41]),
        _custom=bytes([43]),
) -> bytes:
    if isinstance(value, str):
        md = hashlib.new(algo)
        md.update(_string)
        md.update(value.encode('utf8'))
        return md.digest()
    if isinstance(value, bool):
        md = hashlib.new(algo)
        if value:
            md.update(_true)
        else:
            md.update(_false)
        return md.digest()
    if isinstance(value, int):
        md = hashlib.new(algo)
        if value == 0:
            md.update(_zero)
        elif value < 0:
            value *= -1
            md.update(_int_neg)
        else:
            md.update(_int_pos)
        while value > 0:
            md.update(bytes([value % 256]))
            value //= 256
        return md.digest()
    if isinstance(value, float):
        md = hashlib.new(algo)
        md.update(_double)
        md.update(struct.pack("d", value))
        return md.digest()
    if isinstance(value, (list, tuple)):
        md = hashlib.new(algo)
        md.update(_seq)
        for item in value:
            md.update(hash_complex(item, algo=algo))
        return md.digest()
    if isinstance(value, (set, frozenset)):
        md = hashlib.new(algo)
        md.update(_set)
        hashes = []
        for item in value:
            hashes.append(hash_complex(item, algo=algo))
        hashes.sort()
        for h in hashes:
            md.update(h)
        return md.digest()
    if isinstance(value, dict):
        md = hashlib.new(algo)
        if _prefix is None:
            md.update(_map)
        else:
            md.update(_prefix)
        _seq = []
        for key, value in value.items():
            _seq.append((hash_complex(key, algo=algo), hash_complex(value, algo=algo)))
        _seq.sort()
        for key, value in _seq:
            md.update(key)
            md.update(value)
        return md.digest()
    if isinstance(value, (bytes, bytearray)):
        md = hashlib.new(algo)
        md.update(_arbitrary)
        md.update(value)
        return md.digest()
    if value is None:
        md = hashlib.new(algo)
        md.update(_none)
        return md.digest()
    if hasattr(value, '__class__'):
        prefix = bytearray()
        prefix.extend(_custom)
        prefix.extend(hash_complex(value.__class__.__module__, algo=algo))
        prefix.extend(hash_complex(value.__class__.__name__, algo=algo))
        return hash_complex(value.__dict__, algo=algo, _prefix=prefix)
    raise ValueError(value)


def cached_function(func):
    _empty_args_hash = hash_complex(((), {}), algo='sha1').hex()
    _cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args and not kwargs:
            args_hash = _empty_args_hash
        else:
            args_hash = hash_complex((args, kwargs), algo='sha1').hex()
        try:
            result = _cache[args_hash]
        except KeyError:
            result = func(*args, **kwargs)
            _cache[args_hash] = result
        return result

    return wrapper


def cached_method(func):
    _empty_args_hash = hash_complex(((), {}), algo='sha1').hex()

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            cache = self.__method_cache__
        except AttributeError:
            self.__method_cache__ = {}
            cache = self.__method_cache__
        if not args and not kwargs:
            args_hash = _empty_args_hash
        else:
            args_hash = hash_complex((args, kwargs), algo='sha1').hex()
        name = f"{func.__name__}:{args_hash}"
        try:
            result = cache[name]
        except KeyError:
            result = func(self, *args, **kwargs)
            cache[name] = result
        return result

    return wrapper


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def select(obj, *path, fallback=None):
    current = obj
    for element in path:
        try:
            current = current[element]
        except (KeyError, TypeError):
            return fallback
    return current


def substitute(thing, callback: Callable[[str], str]):
    if isinstance(thing, (type(None), bool, int, float)):
        return thing
    if isinstance(thing, str):
        fs = re.split(r"<<(\$?[a-zA-Z0-9-_]+(\.[a-zA-Z0-9-_]+)*)>>", thing)
        result = []
        ix = 0
        for f in fs:
            ix = (ix + 1) % 3
            if ix == 2:
                result.append(callback(f))
            elif ix == 1:
                result.append(f)
        return "".join(result)
    elif isinstance(thing, list):
        result = []
        for item in thing:
            result.append(substitute(item, callback))
        return result
    else:
        result = {}
        for key, value in thing.items():
            key = substitute(key, callback)
            value = substitute(value, callback)
            result[key] = value
        return result


def merge(*objects):
    if all(isinstance(item, list) for item in objects):
        result = []
        for ls in objects:
            for item in ls:
                result.append(item)
        return result
    if not all(isinstance(item, dict) for item in objects):
        raise NoMergePossible()
    result = {}
    for obj in objects:
        for key, value in obj.items():
            if key not in result:
                result[key] = value
                continue
            if isinstance(value, list):
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
            if isinstance(result[key], list):
                if isinstance(value, list):
                    for item in value:
                        result[key].append(item)
                    continue
                result[key].append(value)
                continue
            if isinstance(result[key], dict):
                if not isinstance(value, dict):
                    raise NoMergePossible()
                for item_key, item_value in value.items():
                    result[key][item_key] = item_value
                continue
            result[key] = value
    return result


def parse_name(name) -> List[str]:
    parts = []
    for p1 in str(name).split("-"):
        for part in p1.split("_"):
            current_part = []
            last_was_upper = False
            for char in part:
                if char.isupper() and not last_was_upper:
                    if current_part:
                        parts.append("".join(current_part).lower())
                    current_part = []
                elif char.islower() and last_was_upper:
                    last = current_part.pop()
                    if current_part:
                        parts.append("".join(current_part).lower())
                    current_part = [last]
                current_part.append(char)
                last_was_upper = char.isupper()
            if current_part:
                parts.append("".join(current_part).lower())
    return parts


def simplify_dict(thing):
    try:
        items = thing.items()
    except AttributeError:
        return None
    result = {}
    for key, value in items:
        result[key] = simplify(value)
    return result


def simplify(thing):
    if thing is None:
        return thing
    if isinstance(thing, (bool, str, int, float, Decimal)):
        return thing
    if isinstance(thing, Dezimal):
        if thing.scale == 0:
            return int(thing)
        else:
            return Decimal(str(thing))
    # noinspection PyTypeChecker
    result = simplify_dict(thing)
    if result is not None:
        return result
    # noinspection PyTypeChecker
    return [simplify(elem) for elem in thing]


def empty(value) -> bool:
    if isinstance(value, (bool, list, dict, str)):
        return not value
    return value is None


def convert_num(value, totype):
    if isinstance(totype, (list, tuple)):
        for t in totype:
            try:
                return convert_num(value, t)
            except TypeError:
                pass
    elif isinstance(value, totype):
        return value
    elif issubclass(totype, (int, float, str)):
        return totype(value)
    elif issubclass(totype, (decimal.Decimal, dezimal.Dezimal)):
        return decimal.Decimal(str(value))
    raise TypeError(f"{value} of type {type(value)} can not be converted to {totype}")


def treat(value, *, numtype):
    def rtreat(val):
        if isinstance(val, (str, bool)) or val is None:
            return val
        if isinstance(val, dict):
            for k in val:
                val[k] = rtreat(val[k])
            return val
        if isinstance(val, list):
            for i in range(0, len(val)):
                val[i] = rtreat(val[i])
            return val
        if isinstance(val, (int, float, decimal.Decimal, dezimal.Dezimal)):
            return convert_num(val, numtype)
        raise TypeError(f"Do not know how to process {val} of type {type(val)}")

    return rtreat(value)


JsonValue = Union[type(None), bool, int, float, str, List['JsonValue'], Dict[str, 'JsonValue']]
