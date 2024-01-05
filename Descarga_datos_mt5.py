import MetaTrader5 as mt5
import pandas as pd
import pytz
from datetime import datetime
import pickle

# Cargar las credenciales desde el archivo pickle
with open('credenciales.pkl', 'rb') as f:
    login, password, server = pickle.load(f)

if not mt5.initialize(login=login, password=password, server=server):
    print('Error al inicializar MetaTrader5')
    mt5.shutdown()

lasttick=mt5.symbol_info_tick("NDX")

'''
    time: La marca de tiempo en segundos del último tick.
    bid: El precio de oferta actual para el símbolo financiero.
    ask: El precio de venta actual para el símbolo financiero.
    last: El precio de la última operación. En este caso, parece ser 0.0, lo que indica que no se ha realizado ninguna operación recientemente.
    volume: El volumen de la última operación.
    time_msc: La marca de tiempo en milisegundos del último tick.
    flags: Indicadores adicionales sobre el tick.
    volume_real: El volumen de la última operación en términos reales.

    FLAGS:
    1-FLAG_BID: El precio de oferta ha cambiado.
    2-FLAG_ASK: El precio de venta ha cambiado.
    3-FLAG_LAST: El precio de la última operación ha cambiado.
    4-FLAG_VOLUME: El volumen de la última operación ha cambiado.
    5-FLAG_BUY: El precio de compra ha cambiado.
    6-FLAG_SELL: El precio de venta ha cambiado.
    

   
    '''

bid = lasttick.bid
ask = lasttick.ask

# Funcion para recibir informacion de ticks
def cotizacion(symbol,price='bid'):
    lasttick=mt5.symbol_info_tick(symbol)
    if price=='bid':
        return lasttick.bid
    elif price=='ask':
        return lasttick.ask
    else:
        return None

ticker = 'NDX'

bid = cotizacion(ticker,'bid')
ask = cotizacion(ticker,'ask')
spread = cotizacion(ticker,'ask')-cotizacion(ticker,'bid')

cotizacion(ticker)



# establecer zona horaria en UTC
timezone = pytz.timezone("Etc/UTC")

datetime.now() 
datetime.now(timezone) 




''' TICKS 

copy_ticks_from
copy_ticks_range

'''

#copy_ticks_from
utc_from = datetime(2023, 4, 9, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
n_ticks = 100000000
ticks = mt5.copy_ticks_from(ticker, utc_from, n_ticks, mt5.COPY_TICKS_ALL)  # COPY_TICKS_ALL( todos los ticks disponibles), 
                                                                            # COPY_TICKS_INFO (ticks que contienen cambios en el precio), 
                                                                            # COPY_TICKS_TRADE (ticks que contienen últimos cambios de precio y/o volumen)
len(ticks)

#----------------------------------------

#copy_ticks_range
utc_from = datetime(2023, 11, 1, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
utc_to = datetime(2023, 11, 4, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
utc_to = datetime.now(timezone) 

ticks = mt5.copy_ticks_range(ticker, utc_from, utc_to, mt5.COPY_TICKS_ALL) 
len(ticks)

#----------------------------------------

# Convertimos a dataframe y tratamos los datos
ticks = pd.DataFrame(ticks)

ticks['time']=pd.to_datetime(ticks['time'], unit='s')
ticks['time_msc']=pd.to_datetime(ticks['time_msc'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S.%f')

ticks.set_index('time')
ticks.set_index('time_msc')

ticks.loc[1,'time']
ticks.loc[2,'time']
ticks.loc[1,'time'] == ticks.loc[2,'time']

ticks = ticks.set_index('time_msc')

ticks = ticks.drop('flags', axis=1)
ticks = ticks.drop('time', axis=1)
ticks = ticks.drop('volume_real', axis=1)
ticks = ticks.drop('last', axis=1)
ticks = ticks.drop('volume', axis=1)

ticks = ticks.rename_axis('time')


''' Candlesticks 

copy_rates_from
copy_rates_from_pos
copy_rates_range

'''
# pd.set_option('display.max_columns', 500) # numero maximo de columnas a mostrar
# pd.set_option('display.width', 1500)      # numero maximo de caracteres en una fila
# pd.set_option('display.max_rows', 1000)    # numero maximo de filas a mostrar

#copy_rates_from
utc_from = datetime(2020, 1, 1, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
n_velas = 70000000

timeframe = mt5.TIMEFRAME_M1
'''
TIMEFRAME_M1, TIMEFRAME_M2, TIMEFRAME_M3, TIMEFRAME_M4, TIMEFRAME_M5, TIMEFRAME_M6, 
TIMEFRAME_M10, TIMEFRAME_M12, TIMEFRAME_M15, TIMEFRAME_M20, TIMEFRAME_M30, 
TIMEFRAME_H1, TIMEFRAME_H2, TIMEFRAME_H3, TIMEFRAME_H4, TIMEFRAME_H6, TIMEFRAME_H8, TIMEFRAME_H12,
TIMEFRAME_D1, TIMEFRAME_W1, TIMEFRAME_MN1
'''

data = mt5.copy_rates_from(ticker, timeframe, utc_from, n_velas)

len(data)

#----------------------------------------

# copy_rates_from_pos
pos_vela = 0
n_velas = 10000


data = mt5.copy_rates_from_pos(ticker, timeframe, pos_vela, n_velas)

len(data)

#----------------------------------------

# copy_rates_range
utc_from = datetime(2020, 1, 1, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
utc_to = datetime(2023, 1, 1, tzinfo=timezone) # Formato: aaaa,mm,dd,hh,mm,ss
utc_to = datetime.now(timezone)

data = mt5.copy_rates_range(ticker, timeframe, utc_from, utc_to)

len(data)

#----------------------------------------

# Convertimos a dataframe y tratamos los datos
data = pd.DataFrame(data)

data['time']=pd.to_datetime(data['time'], unit='s')
data = data.set_index('time')

data = data.drop('real_volume', axis=1)
data = data.rename(columns={'tick_volume':'volume'})

data = data.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})
data = data.rename_axis('Date')



