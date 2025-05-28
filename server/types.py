import inspect
from typing import Callable, List, Optional, Dict, Union

from typing import get_origin, get_args, Union, List, Optional


def matches_type(value, expected_type) -> bool:
    # Handle Optional[T]
    origin = get_origin(expected_type)
    args = get_args(expected_type)
    #
    # if len(args) > 1:
    #     print("REecusion")
    # print(origin)
    # print(args)
    if origin is Union and type(None) in args:
        non_none_types = [t for t in args if t is not type(None)]
        if value is None:
            return True
        return any(matches_type(value, t) for t in non_none_types)

    # Handle List[T]
    if origin in (list, List):
        if not isinstance(value, list):
            return False

        print(args)
        inner_type = args[0] if args else object
        return all(matches_type(item, inner_type) for item in value)

    # Handle basic types
    if expected_type in {int, str, float, bool, dict, list}:
        return isinstance(value, expected_type)

    return True  # fallback for untyped or unknown


def validate_arg_types(func, args: dict) -> bool:
    sig = inspect.signature(func)

    for name, param in sig.parameters.items():
        expected = param.annotation
        if expected is inspect.Parameter.empty:
            continue  # untyped

        actual = args.get(name)
        if not matches_type(actual, expected):
            raise Exception(f"{name} expected type {expected}")

    return True


# def coerce_list(value):
#     if value:
#         if isinstance(list, List):
#             return value
#         elif
#     else:
#         return []


def coerce_args(func: Callable, args: dict):
    sig = inspect.signature(func)

    print(sig.parameters)

    for k, v in sig.parameters.items():
        if v.annotation != type(args[k]):
            print(f"{k} should be of type v.annotation")
        print(k, v.annotation, args[k])


def test_function(
    a: Optional[int],
    b: List[str],
    c: str,
    d: float,
    e: Dict[str, List[int]],
    f: bool,
    g: Union[int, str],
):
    pass


args = {
    "a": None,
    "b": ["a"],
    "c": "b",
    "d": 9.0,
    "e": {"k": 9},
    "f": False,
    "g": 1,
}
args_2 = {
    "a": 1,
    "b": ["a"],
    "c": "b",
    "d": 9.0,
    "e": {"k": 9},
    "f": False,
    "g": "1",
}
args_invalid = {
    "a": None,
    "b": 9,
    "c": 9,
    "d": 9.0,
    "e": {"k": 9},
    "f": False,
    "g": 1,
}

print(validate_arg_types(test_function, args))
# coerce_list([1, 2, 3])
# coerce_list(None)
# coerce_list(1)
