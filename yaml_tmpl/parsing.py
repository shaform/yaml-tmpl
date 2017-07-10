from collections import OrderedDict
from collections.abc import Mapping
from numbers import Number

import yaml

from jinja2.sandbox import SandboxedEnvironment

from .namespace import ScopedNamespace


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    https://stackoverflow.com/a/21912744
    """

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)


def update_context(context):
    pass


class Parser(object):
    def __init__(self, env=None):
        self._env = env or SandboxedEnvironment()

    def parse(self, obj, context=None):
        if context is None:
            context = ScopedNamespace()

        if isinstance(obj, str):
            return self._env.from_string(obj).render(context)
        if isinstance(obj, Number):
            return obj
        elif isinstance(obj, (list, tuple)):
            items = []
            for item in obj:
                extendable = isinstance(item, Mapping)
                parsed_item = self.parse(item, context=context)

                if isinstance(parsed_item, (list, tuple)) and extendable:
                    items.extend(parsed_item)
                else:
                    items.append(parsed_item)
            return items
        elif isinstance(obj, Mapping):
            if '_range' in obj:
                range_args = obj['_range']
                if not isinstance(range_args, (list, tuple)):
                    range_args = [range_args]
                return list(range(*[int(self.parse(n, context=context))
                                    for n in range_args]))
            elif '_with_items' in obj:
                with_items_args = obj['_with_items']
                if not isinstance(with_items_args, (list, tuple)):
                    with_items_args = [with_items_args]

                with_items_args = [self.parse(item, context=context)
                                   for item in with_items_args]
                context.open_scope()
                items = []
                obj_copy = dict(obj)
                del obj_copy['_with_items']
                for item in with_items_args:
                    context.item = item
                    items.append(self.parse(obj_copy, context=context))
                context.close_scope()

                return items
            else:
                return {self.parse(key, context=context):
                        self.parse(value, context=context)
                        for key, value in obj.items()}

        else:
            raise NotImplementedError('unable to parse %r' % obj)


config_parser = Parser()
