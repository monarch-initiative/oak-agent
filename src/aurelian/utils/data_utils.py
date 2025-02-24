from typing import Dict, List, Optional, Union

from linkml_runtime.dumpers import json_dumper
from linkml_runtime.utils.yamlutils import YAMLRoot
from pydantic import BaseModel


def flatten(d: Dict, preserve_keys: Optional[List] = None) -> Dict:
    """Flatten a dictionary"""
    out = {}
    for k, v in d.items():
        if isinstance(v, list):
            if preserve_keys and k in preserve_keys:
                out[k] = [flatten(x, preserve_keys=preserve_keys) for x in v]
            else:
                out[f"{k}_count"] = len(v)
        elif isinstance(v, dict):
            out[k] = flatten(v, preserve_keys=preserve_keys)
        else:
            out[k] = v
    return out


def obj_to_dict(obj: Union[object, YAMLRoot, BaseModel, Dict]) -> Dict:
    if isinstance(obj, YAMLRoot):
        return json_dumper.to_dict(obj)
    elif isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return obj
    else:
        raise ValueError(f"Cannot convert object of type {type(obj)} to dict")
