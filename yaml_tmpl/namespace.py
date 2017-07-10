from collections.abc import MutableMapping
from collections import defaultdict


class Namespace(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = dict()
        self._prefix = ''
        self._ref_count = defaultdict(int)
        self.update(*args, **kwargs)

    def _update_ref_count(self, key, count):
        while '.' in key:
            key = key.rsplit('.', 1)[0]
            self._ref_count[key] += count
            assert self._ref_count[key] >= 0

    def _transform_key(self, key):
        if self._prefix:
            return self._prefix + key
        else:
            return key

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for name, value in self._store.items():
            if name.isidentifier():
                arg_strings.append('%s=%r' % (name, value))
            else:
                star_args[name] = value
        if star_args:
            arg_strings.append('**%s' % repr(star_args))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def __getitem__(self, key):
        key = self._transform_key(key)
        if key not in self._store or self._ref_count[key] > 0:
            view = self.__class__()
            view._store = self._store
            view._ref_count = self._ref_count
            view._prefix = key + '.'
            return view
        return self._store[key]

    def __setitem__(self, key, value):
        key = self._transform_key(key)
        if key not in self._store:
            self._update_ref_count(key, 1)
        self._store[key] = value

    def __delitem__(self, key):
        key = self._transform_key(key)
        if key in self._store:
            self._update_ref_count(key, -1)
        del self._store[key]

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, name))
        else:
            return self.__getitem__(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self.__setitem__(name, value)

    def __delattr__(self, name):
        self.__delitem__(name)

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)


class ScopedNamespace(Namespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scope_level = 0

    def open_scope(self):
        self._scope_level += 1

    def close_scope(self):
        self._scope_level -= 1

    def __getitem__(self, key):
        self.__delitem__(key, level=self._scope_level + 1)
        items = super().__getitem__(key)
        if isinstance(items, Namespace):
            return items
        else:
            return items[-1][0]

    def __setitem__(self, key, value):
        self.__delitem__(key)
        item = (value, self._scope_level)
        items = super().__getitem__(key)
        if isinstance(items, Namespace):
            super().__setitem__(key, [item])
        else:
            items.append(item)

    def __delitem__(self, key, level=None):
        items = super().__getitem__(key)
        if isinstance(items, list):
            if level is None:
                level = self._scope_level
            while items and items[-1][1] >= level:
                items.pop()
            if items:
                super().__setitem__(key, items)
            else:
                super().__delitem__(key)
