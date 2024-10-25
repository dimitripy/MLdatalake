# ggf. als unterfunktion für "load_and_process_data_from_csv" verwenden
# #alte Funktion ohne chunks zu laden
#Stand veralet
def process_and_insert_data(session, bars1m, symbol_filter=None):
    if symbol_filter:
        bars1m = bars1m.query(f'ticker == "{symbol_filter}"')
    
    # Resample auf 1-Minuten-Intervalle
    bars1m = bars1m.reset_index().set_index('date').groupby('ticker').resample('1min').last().droplevel(0)
    bars1m.loc[:, bars1m.columns[:-1]] = bars1m[bars1m.columns[:-1]].ffill()
    bars1m.loc[:, 'volume'] = bars1m['volume'].fillna(value=0.0)
    bars1m = bars1m.reset_index().sort_values(by=['date', 'ticker']).set_index(['date', 'ticker'])
    
    tickers = bars1m.index.get_level_values(1).unique()
    latest_date = bars1m.index.get_level_values('date').max()
    active_tickers = bars1m.loc[latest_date].index.get_level_values('ticker').unique()
    
    symbols = pd.DataFrame(tickers, columns=['ticker'])
    symbols['name'] = symbols['ticker']
    symbols['market'] = 'crypto'
    symbols['active'] = np.where(symbols['ticker'].isin(active_tickers), True, False)
    symbols = symbols.sort_values(by='ticker')
    
    total_symbols = len(symbols)
    for i, r in symbols.iterrows():
        try:
            print(f"Uploading symbol {i+1}/{total_symbols}: {r['ticker']}")
            
            symbol = af.Symbol(ticker=r['ticker'], name=r['name'], market=af.Market[r['market']], active=r['active'])
            session.add(symbol)
            session.commit()
            
            # Überprüfen, ob der Index existiert
            if r['ticker'] in bars1m.index.get_level_values('ticker'):
                bars = bars1m.xs(r['ticker'], level='ticker').reset_index()
                bars['symbol_id'] = symbol.id
                
                session.bulk_insert_mappings(af.MinuteBar, bars.to_dict(orient='records'))
                session.commit()
            else:
                print(f"Ticker {r['ticker']} nicht im Index gefunden.")
        except Exception as e:
            print(f"An error occurred while uploading symbol {r['ticker']}: {e}")
            session.rollback()