import unittest

from ..parsing import config_parser


class TestRange(unittest.TestCase):
    def test_range(self):
        checks = [
            ({'k': {'_range': [4]}}, {'k': list(range(4))}),
            ({'k': [{'_range': 4}]}, {'k': list(range(4))}),
            ({'k': [{'_range': [4]}]}, {'k': list(range(4))}),
            ({'k': {'_range': [0, 4]}}, {'k': list(range(4))}),
            ({'k': {'_range': [0, 4, 2]}}, {'k': list(range(0, 4, 2))}),
            ({'k': [{'_range': 2}, {'_range': [2, 4]}]}, {'k':
                                                          list(range(4))}),
            ({'k': [{'_range': 2}, {'_range': [2, 4]}]}, {'k':
                                                          list(range(4))}),
        ]
        for pre_render, post_render in checks:
            self.assertEqual(
                config_parser.parse(pre_render), post_render, pre_render)

    def test_items(self):
        checks = [
            ({'k': {'_with_items': [1, 2, 'x'],
                    'name': '{{ item }} says'}},
             {'k': [{'name': '1 says'}, {'name': '2 says'}, {'name': 'x says'}]
              }),
        ]
        for pre_render, post_render in checks:
            self.assertEqual(
                config_parser.parse(pre_render), post_render, pre_render)


if __name__ == '__main__':
    unittest.main()
