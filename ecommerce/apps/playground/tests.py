import unittest
from unittest.mock import MagicMock, Mock, patch

from .playground import do_something


class TestPlayground(unittest.TestCase):
    @patch('ecommerce.apps.playground.foo.foo')
    def test_foobar(self, mock_foo):
        mock_foo.return_value = 24
        self.assertEquals(do_something(), 24)
