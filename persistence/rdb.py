import os
import time
import pickle
from typing import Dict, Tuple, Any

def dump(data: Dict[bytes, Any], expiry: Dict[bytes, float], path: str) -> None:
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "wb") as f:
            pickle.dump((data, expiry), f)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

def load(path: str) -> Tuple[Dict[bytes, Any], Dict[bytes, float]]:
    if not os.path.exists(path):
        return {}, {}
    with open(path, "rb") as f:
        data, expiry = pickle.load(f)
    now = time.time() * 1000
    for key in list(expiry.keys()):
        if expiry[key] <= now:
            del expiry[key]
            data.pop(key, None)
    return data, expiry