# schemas.py

SCHEMAS = {
    'Yahoo Finance': {
        'source': 'Yahoo Finance',
        'required_columns': ['date', 'symbol_id', 'open', 'high', 'low', 'close', 'volume']
    },
    'Another Source': {
        'source': 'Another Source',
        'required_columns': ['date', 'symbol', 'open_price', 'high_price', 'low_price', 'closing_price', 'volume']
    }
}