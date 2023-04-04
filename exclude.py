import pickle
from typing import List, Optional
import re

UNRESTRICTED = 'unrestricted'
FIXED = 'fixed'
NOTHING = 'nothing'

def _get_text_number(text):
    match = re.match(r'(.+?)(\d+)', text) # match any text and number parts
    if match:
        return (match.group(1), int(match.group(2))) # return them as a tuple
    else:
        return (text, 0) # return the original string and zero if no match

class Exclude:
    FILENAME = 'exclude'
    unrestricted = []
    fixed = []
    nothing = []
    _loaded = False

    def __init__(self):
        if not Exclude._loaded:
            self._load()

    def _load(self):
        try:
            with open(Exclude.FILENAME, 'rb') as f:
                a, b, c = pickle.load(f)
        except FileNotFoundError:
            self._new()
        else:
            Exclude.unrestricted = a
            Exclude.fixed = b
            Exclude.nothing = c
            Exclude._loaded = True

    def _save(self):
        save = [Exclude.unrestricted, Exclude.fixed, Exclude.nothing]
        with open(Exclude.FILENAME, 'wb') as f:
            pickle.dump(save, f)

    def _new(self):
        with open(Exclude.FILENAME, 'xb') as f:
            pickle.dump([[],[],[]], f)
        self._load()

    def unrestricted_list(self) -> list: ret = Exclude.unrestricted.sort(key=_get_text_number); return ret
    
    def fixed_list(self) -> list: ret = Exclude.fixed.sort(key=_get_text_number); return ret
    
    def nothing_list(self) -> list: ret = Exclude.nothing.sort(key=_get_text_number); return ret
    
    def remove(self, name):
        if name in Exclude.fixed: Exclude.fixed.remove(name)
        if name in Exclude.nothing: Exclude.nothing.remove(name)
        if name in Exclude.unrestricted: Exclude.unrestricted.remove(name)
        self._save()
    
    def _run_on_add(func):
        def wrapper(self, name):
            self.remove(name)
            func(self, name)
            self._save()
        return wrapper

    @_run_on_add
    def add_to_unrestricted(self, name: str):
        Exclude.unrestricted.append(name)

    @_run_on_add
    def add_to_fixed(self, name: str):
        Exclude.fixed.append(name)

    @_run_on_add
    def add_to_nothing(self, name: str):
        Exclude.nothing.append(name)

    def get_exclude_type(self, name) -> Optional[List[str]]:
        ret = []
        if name in Exclude.fixed: ret.append(FIXED)
        if name in Exclude.nothing: ret.append(NOTHING)
        if name in Exclude.unrestricted: ret.append(UNRESTRICTED)
        if ret: return ret
        else: return None

    def get_all_exclude(self) -> List[str]:
        """This function will return all the names with sorted"""
        ret = Exclude.fixed + Exclude.unrestricted + Exclude.nothing
        ret.sort(key=_get_text_number)
        return ret

# for testing purposes
if __name__ == '__main__':
    exclude = Exclude()
    pass