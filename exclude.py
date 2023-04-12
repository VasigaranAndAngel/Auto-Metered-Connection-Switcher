import pickle
from typing import List, Optional, Literal
import re

UNRESTRICTED = 'unrestricted'
FIXED = 'fixed'
NOTHING = 'nothing'
OFF = 'off'

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
    off = []
    _loaded = False

    def __init__(self):
        if not Exclude._loaded:
            self._load()

    def _load(self):
        try:
            with open(Exclude.FILENAME, 'rb') as f:
                a, b, c, d = pickle.load(f)
        except FileNotFoundError:
            self._new()
        else:
            Exclude.unrestricted = a
            Exclude.fixed = b
            Exclude.nothing = c
            Exclude.off = d
            Exclude._loaded = True

    def _save(self):
        save = [Exclude.unrestricted, Exclude.fixed, Exclude.nothing, Exclude.off]
        with open(Exclude.FILENAME, 'wb') as f:
            pickle.dump(save, f)

    def _new(self):
        with open(Exclude.FILENAME, 'xb') as f:
            pickle.dump([[],[],[],[]], f)
        self._load()

    def unrestricted_list(self) -> List[str]:"""Returns the unrestricted list"""; ret = Exclude.unrestricted.sort(key=_get_text_number); return ret
    
    def fixed_list(self) -> List[str]:"""Returns the fixed list"""; ret = Exclude.fixed.sort(key=_get_text_number); return ret
    
    def nothing_list(self) -> List[str]:"""Returns the nothing list"""; ret = Exclude.nothing.sort(key=_get_text_number); return ret

    def off_list(self) -> List[str]:"""Returns the off list"""; ret = Exclude.off.sort(key=_get_text_number); return ret
    
    def remove(self, name, _from:Literal['unrestricted', 'fixed', 'nothing', 'off', 'all']):
        """Removes the given name from the list if it exists in any of the lists"""
        if (_from==FIXED or _from=='all') and name in Exclude.fixed: Exclude.fixed.remove(name)
        if (_from==NOTHING or _from=='all') and name in Exclude.nothing: Exclude.nothing.remove(name)
        if (_from==UNRESTRICTED or _from=='all') and name in Exclude.unrestricted: Exclude.unrestricted.remove(name)
        if (_from==OFF or _from=='all') and name in Exclude.off: Exclude.off.remove(name)
        self._save()
    
    def _run_on_add(func):
        def wrapper(self, name):
            self:Exclude = self
            if self.get_exclude_type(name):
                self.remove(name, self.get_exclude_type(name)[0])
            func(self, name)
            self._save()
        return wrapper

    @_run_on_add
    def add_to_unrestricted(self, name: str):
        """Adds the given name to the unrestricted list and removes it from other list if exist."""
        Exclude.unrestricted.append(name)

    @_run_on_add
    def add_to_fixed(self, name: str):
        """Adds the given name to the fixed list and removes it from other list if exist."""
        Exclude.fixed.append(name)

    @_run_on_add
    def add_to_nothing(self, name: str):
        """Adds the given name to the nothing list and removes it from other list if exist."""
        Exclude.nothing.append(name)

    def add_to_off(self, name: str):
        """Adds the given name to the off list."""
        if not name in Exclude.off:
            Exclude.off.append(name)
            self._save()

    def get_exclude_type(self, name: str) -> Optional[List[Literal['fixed', 'nothing', 'unrestricted', 'off']]]:
        """Returns the type of the exclude of the given name. returns None if the name does not exist in the list"""
        ret = []
        if name in Exclude.fixed: ret.append(FIXED)
        if name in Exclude.nothing: ret.append(NOTHING)
        if name in Exclude.unrestricted: ret.append(UNRESTRICTED)
        if name in Exclude.off: ret.append(OFF)
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