from typing import List, Dict, Callable
import pandas as pd
import uuid
import hashlib


def __df_col_assign(df: pd.DataFrame, replace: bool, col: str, suffix: str, values: List):
    if replace:
        df.drop(columns=[col], inplace=True)
        df[col] = values
    else:
        df[col + suffix] = values


def trunc_hash(value_list: List, salt: str) -> List[str]:
    encoded_salt = salt.encode()
    hash_values = []
    for value in value_list:
        m = hashlib.sha512()
        m.update(encoded_salt)
        m.update(str(value).encode())
        hash_values.append(m.hexdigest()[:32])
    return hash_values


def trunc_hash_dataframe(df: pd.DataFrame, columns: Dict[str, str], replace=False,
                         suffix="_anonymized"):
    for col, salt in columns.items():
        __df_col_assign(df, replace, col, suffix, trunc_hash(df[col], salt))


def anonymize(value_list: List, generate: Callable) -> List:
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


def anonymize_dataframe(df: pd.DataFrame, columns: Dict[str, Callable], replace=False, suffix="_anonymized"):
    for col, gen in columns.items():
        __df_col_assign(df, replace, col, suffix, anonymize(df[col], gen))


def anonymize_uuid(value_list: List) -> List[uuid.UUID]:
    return anonymize(value_list, uuid.uuid4)


def anonymize_dataframe_uuid(df: pd.DataFrame, columns: List[str], replace=False, suffix="_anonymized"):
    anonymize_dataframe(df, dict(zip(columns, [uuid.uuid4] * len(columns))), replace=replace, suffix=suffix)
