
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
from dags.modules.Grabber.Asset_src.YahooFinance import load_yf_data, transform_data

class TestYahooFinance(unittest.TestCase):

    @patch('yfinance.Ticker')
    def test_load_yf_data_success(self, mock_yf_ticker):
        # Mocking the yfinance Ticker object and its history method
        mock_ticker = MagicMock()
        mock_yf_ticker.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame({
            'Datetime': pd.date_range(start='2024-10-02', periods=5, freq='D'),
            'Open': [100, 101, 102, 103, 104],
            'High': [110, 111, 112, 113, 114],
            'Low': [90, 91, 92, 93, 94],
            'Close': [105, 106, 107, 108, 109],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })

        row = {
            'ticker': 'AAPL',
            'last_update': '2024-10-01',
            'timeframe': '1d'
        }

        result = load_yf_data(row)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)

    @patch('yfinance.Ticker')
    def test_load_yf_data_no_data(self, mock_yf_ticker):
        # Mocking the yfinance Ticker object and its history method to return an empty DataFrame
        mock_ticker = MagicMock()
        mock_yf_ticker.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()

        row = {
            'ticker': 'AAPL',
            'last_update': '2024-10-01',
            'timeframe': '1d'
        }

        result = load_yf_data(row)
        self.assertIsNone(result)

    def test_transform_data_success(self):
        data = pd.DataFrame({
            'Datetime': pd.date_range(start='2024-10-02', periods=5, freq='D'),
            'Open': [100, 101, 102, 103, 104],
            'High': [110, 111, 112, 113, 114],
            'Low': [90, 91, 92, 93, 94],
            'Close': [105, 106, 107, 108, 109],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })

        symbol_id = 'AAPL'
        result = transform_data(data, symbol_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)

    def test_transform_data_key_error(self):
        data = pd.DataFrame({
            'Date': pd.date_range(start='2024-10-02', periods=5, freq='D'),
            'Open': [100, 101, 102, 103, 104],
            'High': [110, 111, 112, 113, 114],
            'Low': [90, 91, 92, 93, 94],
            'Close': [105, 106, 107, 108, 109],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })

        symbol_id = 'AAPL'
        result = transform_data(data, symbol_id)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()