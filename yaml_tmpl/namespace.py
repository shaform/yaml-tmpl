from collections.abc import MutableMapping


class Namespace(MutableMapping):
    def __init__(self, *args, **kwargs):
        super().__setattr__('_store', dict(*args, **kwargs))

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
        return self._store.setdefault(key, Namespace())

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, name))
        else:
            return self.__getitem__(name)

    def __setattr__(self, name, value):
        self.__setitem__(name, value)

    def __delattr__(self, name):
        self.__delitem__(name)

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)
