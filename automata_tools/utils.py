from typing import Dict, Any


def merge_dict(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    dict2.update(dict1)
    return dict2
