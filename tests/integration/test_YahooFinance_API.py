import unittest
import pandas as pd
from datetime import datetime
from dags.modules.Grabber.Asset_src.YahooFinance import load_yf_data, transform_data

class TestYahooFinanceIntegration(unittest.TestCase):

    def test_load_yf_data_integration(self):
        # Hier definieren wir das Test-Row-Dictionary mit den tatsächlichen Daten
        '''            row = {
                'ticker': 'AAPL',
                'last_update': '2024-09-01',  # Beispieldatum, das flexibel angepasst werden kann
                'timeframe': '1d'
            }'''
        row = {
            'ticker': 'AAPL',
            #'ticker': 'EURUSD=X',
            'name': 'Euro-Dollar',
            'market': 'forex',
            'exchange': 'Yahoo Finance',
            'start_date': '2024-09-01',
            'last_update': '2024-10-01',  
            'timeframe': '5m',
            'active': 1
        }

        # Daten abrufen
        data = load_yf_data(row)
        
        # Überprüfen, dass Daten erfolgreich abgerufen wurden
        self.assertIsNotNone(data, "Abruf von Yahoo Finance-Daten fehlgeschlagen.")
        
        # Zusätzliche Überprüfungen auf erwartete Spalten
        self.assertIn('date', data.columns, "Spalte 'date' fehlt im abgerufenen DataFrame.")
        self.assertIn('open', data.columns, "Spalte 'open' fehlt im abgerufenen DataFrame.")
        self.assertIn('high', data.columns, "Spalte 'high' fehlt im abgerufenen DataFrame.")
        self.assertIn('low', data.columns, "Spalte 'low' fehlt im abgerufenen DataFrame.")
        self.assertIn('close', data.columns, "Spalte 'close' fehlt im abgerufenen DataFrame.")
        self.assertIn('volume', data.columns, "Spalte 'volume' fehlt im abgerufenen DataFrame.")
        
        print("Integrationstest abgeschlossen. Abgerufene Daten:")
        print(data.head())

    def test_transform_data_integration(self):
        # Beispiel-Testdaten für die Transformation
        raw_data = pd.DataFrame({
            'Datetime': pd.date_range(start='2024-10-02', periods=5, freq='D'),
            'Open': [100, 101, 102, 103, 104],
            'High': [110, 111, 112, 113, 114],
            'Low': [90, 91, 92, 93, 94],
            'Close': [105, 106, 107, 108, 109],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })

        transformed_data = transform_data(raw_data, 'AAPL')
        
        # Überprüfen, dass die Transformation erfolgreich war
        self.assertIsNotNone(transformed_data, "Transformation der Daten fehlgeschlagen.")
        self.assertEqual(len(transformed_data), 5)
        self.assertIn('open', transformed_data.columns)
        self.assertIn('high', transformed_data.columns)
        self.assertIn('low', transformed_data.columns)
        self.assertIn('close', transformed_data.columns)
        self.assertIn('volume', transformed_data.columns)
        
        print("Transformationsdaten:")
        print(transformed_data.head())

if __name__ == '__main__':
    unittest.main()
