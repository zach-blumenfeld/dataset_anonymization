from typing import List, Dict, Callable
import pandas as pd
import uuid


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
        values = anonymize(df[col], gen)
        if replace:
            df.drop(columns=[col], inplace=True)
            df[col] = values
        else:
            df[col + prefix] = values


def anonymize_uuid(value_list: List):
    return anonymize(value_list, uuid.uuid4)


def anonymize_dataframe_uuid(df: pd.DataFrame, columns: List[str], replace=False, prefix="_anonymized"):
    anonymize_dataframe(df, dict(zip(columns, [uuid.uuid4] * len(columns))), replace=replace, prefix=prefix)
