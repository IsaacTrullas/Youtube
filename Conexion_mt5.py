import MetaTrader5 as mt5
import pandas as pd
import pytz
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import pickle

# Credenciales de conexion
login = 300000000
password ='abcdefghi'
server = 'demoUK-mt5.darwinex.com'

# Guardar las credenciales en un archivo pickle
with open('cuentademo1.pkl', 'wb') as f:
    pickle.dump([login, password, server], f)

# Cargar las credenciales desde el archivo pickle
with open('cuentademo1.pkl', 'rb') as f:
    login, password, server = pickle.load(f)


# Conexion con el servidor

mt5.initialize(login=login, password=password, server=server)



if not mt5.initialize(login=login, password=password, server=server):
    print('Error al inicializar MetaTrader5')
    mt5.shutdown()

# obtener información de un símbolo
symbol_info = mt5.symbol_info('EURUSD')

# Obtener la lista de símbolos disponibles
symbols = mt5.symbols_get()

len(symbols)

# Crear una lista para almacenar los datos de cada símbolo
symbol_data = []

# Iterar a través de todos los símbolos y obtener sus datos
for symbol in symbols:
    # Obtener los datos de cada símbolo
    symbol_info = mt5.symbol_info(symbol.name)
    # Agregar los datos a la lista symbol_data
    symbol_data.append(symbol_info._asdict())

symbol_data[0]
symbol_data[256]

symbol_data[0]['name']
symbol_data[0]['currency_profit']
symbol_data[0]['trade_contract_size']
symbol_data[0]['volume_max']
symbol_data[0]['volume_min']
symbol_data[0]['volume_step']


symbol_data[256]['name']
symbol_data[256]['description']
symbol_data[256]['path']
symbol_data[256]['volume_min']
symbol_data[256]['volume_step']

# Crear un DataFrame los datos de los símbolos
symbol_info = pd.DataFrame(symbol_data)
symbol_info.columns
len(symbol_info.columns)

# Crear un DataFrame con ciertos datos de los símbolos

symbol_info2 = symbol_info[['name', 'description', 'path']]
symbol_info2 = symbol_info2.rename(columns={'name': 'tickers'})

symbol_info2 = symbol_info2.rename(columns={'path': 'type'})
symbol_info2['type'] = symbol_info['path'].apply(lambda x: x.split('\\')[0])


symbol_info2['mercado'] = symbol_info['path'].apply(
                                                    lambda x: x.split('\\')[0] if x.split('\\')[0] in ['Forex', 'Indices', 'ETFs', 'Commodities'] else 
                                                    (x.split('\\')[2] if len(x.split('\\')) > 2 else x.split('\\')[1] if len(x.split('\\')) > 1 else None))

symbol_info2.head(60)


symbol_info2['type'].unique()
symbol_info2['mercado'].unique()

# Creamos variable con los tickers de los indices
indices_tickers = symbol_info2.loc[symbol_info2['type'] == 'Indices']['tickers'].tolist()
len(indices_tickers)

len(symbol_info2.loc[symbol_info2['type'] == 'Indices']['tickers'].tolist())

# Creamos variable con los tickers de los forex
forex_tickers = symbol_info2.loc[symbol_info2['type'] == 'Forex']['tickers'].tolist()
len(forex_tickers)

# Creamos variable con los tickers de los ETFs
etfs_tickers = symbol_info2.loc[symbol_info2['type'] == 'ETFs']['tickers'].tolist()
len(etfs_tickers)

# Creamos variable con los tickers de los Commodities
commodities_tickers = symbol_info2.loc[symbol_info2['type'] == 'Commodities']['tickers'].tolist()
len(commodities_tickers)

