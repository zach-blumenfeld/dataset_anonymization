from typing import List
import pandas as pd
import uuid
import hashlib
import random


def __df_col_assign(df: pd.DataFrame, replace: bool, col: str, suffix: str, values: List):
    if replace:
        df.drop(columns=[col], inplace=True)
        df[col] = values
    else:
        df[col + suffix] = values


def hash_key(value_list: List, passphrase: str) -> List[str]:
    encoded_passphrase = passphrase.encode()
    hash_values = []
    for value in value_list:
        m = hashlib.sha512()
        m.update(encoded_passphrase)
        m.update(str(value).encode())
        hash_values.append(m.hexdigest()[:32])
    return hash_values


def hash_df_key(df: pd.DataFrame, column: str, passphrase: str, replace: bool = False, suffix: str = "_anonymized"):
    __df_col_assign(df, replace, column, suffix, hash_key(df[column], passphrase))


def anonymize(value_list: List) -> List[uuid.UUID]:
    value_map = {}
    anon_values = []
    for value in value_list:
        if value in value_map:
            anon_values.append(value_map[value])
        else:
            anon_value = uuid.uuid4()
            value_map[value] = anon_value
            anon_values.append(anon_value)
    return anon_values


def anonymize_df_col(df: pd.DataFrame, column: str, replace: bool = False, suffix: str = "_anonymized"):
    __df_col_assign(df, replace, column, suffix, anonymize(df[column]))


def anonymize_label(value_list: List, prefix: str = 'TYPE_', postfix: str = '') -> List[str]:
    value_set = set(value_list)
    n = len(value_set)
    enums = [prefix + str(i) + postfix for i in range(1, n + 1)]
    random.shuffle(enums)
    value_map = dict(zip(value_set, enums))
    anon_values = []
    for value in value_list:
        anon_values.append(value_map[value])
    return anon_values


def anonymize_df_label(df: pd.DataFrame, column: str, prefix: str = 'TYPE_', postfix: str = '',
                       replace: bool = False, suffix: str = "_anonymized"):
    __df_col_assign(df, replace, column, suffix, anonymize_label(df[column], prefix=prefix, postfix=postfix))
