from typing import List, Dict, Callable
import pandas as pd
import uuid
import hashlib


def __df_col_assign(df: pd.DataFrame, replace: bool, col: str, prefix: str, values: List):
    if replace:
        df.drop(columns=[col], inplace=True)
        df[col] = values
    else:
        df[col + prefix] = values


def hash512(value_list: List, salt: str, digests_as_strings=False):
    hash_values = []
    for value in value_list:
        m = hashlib.sha512()
        m.update(salt.encode())
        m.update(str(value).encode())
        if digests_as_strings:
            hash_values.append(m.hexdigest())
        else:
            hash_values.append(m.digest())
    return hash_values


def hash512_dataframe(df: pd.DataFrame, columns: Dict[str, str], digests_as_strings=False, replace=False,
                      prefix="_anonymized"):
    for col, salt in columns.items():
        __df_col_assign(df, replace, col, prefix, hash512(df[col], salt, digests_as_strings=digests_as_strings))


def anonymize(value_list: List, generate: Callable):
    value_map = {}
    anon_values = []
    for value in value_list:
        if value in value_map:
            anon_values.append(value_map[value])
        else:
            anon_value = generate()
            value_map[value] = anon_value
            anon_values.append(anon_value)
    return anon_values


def anonymize_dataframe(df: pd.DataFrame, columns: Dict[str, Callable], replace=False, prefix="_anonymized"):
    for col, gen in columns.items():
        __df_col_assign(df, replace, col, prefix, anonymize(df[col], gen))


def anonymize_uuid(value_list: List):
    return anonymize(value_list, uuid.uuid4)


def anonymize_dataframe_uuid(df: pd.DataFrame, columns: List[str], replace=False, prefix="_anonymized"):
    anonymize_dataframe(df, dict(zip(columns, [uuid.uuid4] * len(columns))), replace=replace, prefix=prefix)
