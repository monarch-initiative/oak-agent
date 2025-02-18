from typing import Dict, Optional, List


def flatten(d: Dict, preserve_keys: Optional[List] = None) -> Dict:
    """
    Flatten a dictionary
    """
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
