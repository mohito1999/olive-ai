from typing import Any, Dict

from langchain_core.utils import _merge


def merge_dicts(left: Dict[str, Any], *others: Dict[str, Any]) -> Dict[str, Any]:
    """Merge many dicts, handling specific scenarios where a key exists in both
    dictionaries but has a value of None in 'left'. In such cases, the method uses the
    value from 'right' for that key in the merged dictionary.

    Example:
        If left = {"function_call": {"arguments": None}} and
        right = {"function_call": {"arguments": "{\n"}}
        then, after merging, for the key "function_call",
        the value from 'right' is used,
        resulting in merged = {"function_call": {"arguments": "{\n"}}.
    """
    merged = left.copy()
    for right in others:
        for right_k, right_v in right.items():
            if right_k not in merged:
                merged[right_k] = right_v
            elif right_v is not None and merged[right_k] is None:
                merged[right_k] = right_v
            elif right_v is None:
                continue
            elif type(merged[right_k]) is not type(right_v):
                raise TypeError(
                    f'additional_kwargs["{right_k}"] already exists in this message,'
                    " but with a different type."
                )
            elif isinstance(merged[right_k], str):
                merged[right_k] += right_v
            elif isinstance(merged[right_k], dict):
                merged[right_k] = merge_dicts(merged[right_k], right_v)
            elif isinstance(merged[right_k], list):
                merged[right_k] = _merge.merge_lists(merged[right_k], right_v)
            elif isinstance(merged[right_k], int):
                merged[right_k] = merged[right_k] + right_v
            elif merged[right_k] == right_v:
                continue
            else:
                raise TypeError(
                    f"Additional kwargs key {right_k} already exists in left dict and "
                    f"value has unsupported type {type(merged[right_k])}."
                )
    return merged

_merge.merge_dicts = merge_dicts
