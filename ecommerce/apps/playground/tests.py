import unittest
from unittest.mock import patch

from .base import work


class TestPlayground(unittest.TestCase):
    @patch('ecommerce.apps.playground.service.bar', return_value=24)
    def test_work(self, mock_bar):
        self.assertEquals(work(), 24)
