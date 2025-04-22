SELECT * FROM minute_bar
WHERE symbol_id = 18
-- WHERE symbol_id = (SELECT id FROM symbol WHERE ticker = 'btcusd' LIMIT 1)
-- AND date BETWEEN '2022-11-01' AND '2022-12-31'