from itertools import chain
from typing import List
import re

def greetings(to_be_greeted):
    def hello_msg(*args, **kwargs):
        return f'Hello {str(to_be_greeted(*args, **kwargs)).title()}'
    return hello_msg


def is_palindrome(is_it):
    def maybe(*args, **kwargs):
        test1 = ''
        to_test = str(is_it(*args, **kwargs))
        for i in to_test:
            if i.isalpha() or i.isnumeric():
                test1 += i.lower()
        test2 = test1[::-1]
        if test1 == test2:
            return f'{to_test} - is palindrome'
        else:
            return f'{to_test} - is not palindrome'
    return maybe


def format_output_moj(*args1):
    wha = args1
    if len(wha) < 1:
        raise ValueError

    def the_real_one(change_dict):
        def what_to(*args, **kwargs):
            result = {}
            for i, j in change_dict(*args, **kwargs).items():
                for x, y in change_dict(*args, **kwargs).items():
                    if x != i:
                        result[f'{str(i)}__{str(x)}'] = f'{str(j)} {str(y)}'
            result2 = {}
            for i, j in change_dict(*args, **kwargs).items():
                for x, y in change_dict(*args, **kwargs).items():
                    for k, l in change_dict(*args,**kwargs).items():
                        if x != i and i != k and k != x:
                            result2[f'{str(i)}__{str(x)}__{str(k)}'] = f'{str(j)} {str(y)} {str(l)}'
            result.update(result2.copy())
            result.update(change_dict(*args, **kwargs).copy())
            for k in wha:
                try:
                    result[k]
                except KeyError:
                    raise ValueError
            result_ost = {k: result[k] for k in wha if k in result}
            return result_ost
        return what_to
    return the_real_one


def format_output(*required_keys):
    def decorator(func):
        def build_value(keys: List[List[str]], source_dict: dict):
            values = [source_dict[key] for key in keys]
            return " ".join(values)

        def wrapper(*args):
            dec_arguments = [required_key.split("__") for required_key in required_keys]
            func_output = func(*args)

            if not all(k in func_output.keys() for k in set(chain(*dec_arguments))):
                raise ValueError

            new_output = {}
            for (idx, dec_argument) in enumerate(dec_arguments):
                value = build_value(dec_argument, func_output)
                new_output[required_keys[idx]] = value

            return new_output

        return wrapper

    return decorator


def add_class_method(Cla):
    def true_decoration(func):
        def robi(cls):
            return func()
        setattr(Cla, func.__name__, classmethod(robi))
        return robi
    return true_decoration


def add_instance_method(Cla):
    def true_decoration(func):
        def robi(self):
            return func()
        setattr(Cla, func.__name__, robi)
        return robi
    return true_decoration


# Alternative solution - static method
# def add_class_method(klass):
#     def decorator(func):
#         # @statcimethod
#         def wrapper():
#             return func()

#         # setattr(klass, func.__name__, wrapper)
#         setattr(klass, func.__name__, staticmethod(wrapper))
#         return func

#     return decorator