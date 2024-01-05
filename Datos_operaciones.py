import MetaTrader5 as mt5
import pandas as pd
import pytz
from datetime import datetime
import pickle
import matplotlib.pyplot as plt

# mostrar todas las columnas del dataframe
#pd.set_option('display.max_columns', 500)


# Cargar las credenciales desde el archivo pickle
with open('credenciales.pkl', 'rb') as f:
    login, password, server = pickle.load(f)

if not mt5.initialize(login=login, password=password, server=server):
    print('Error al inicializar MetaTrader5')
    mt5.shutdown()



'''

history_deals_total: Devuelve el número total de operaciones en el historial de la cuenta.
history_deals_get: Devuelve el historial de operaciones de la cuenta con filtros opcionales.
history_orders_total: Devuelve el número total de movimientos de órdenes en el historial de la cuenta.
history_orders_get: Devuelve el historial de movimientos de órdenes de la cuenta con filtros opcionales.
'''


'''History_deals_total()'''
# Devuelve el número total de operaciones en el historial de la cuenta.

date_from = datetime(2023, 4, 1)    # fecha inicial en formato datetime (año, mes, día) en Etc/UTC

timezone = pytz.timezone("Etc/UTC")
date_to = datetime.now(timezone)    # fecha final en formato datetime (año, mes, día) en Etc/UTC

numero_operaciones = mt5.history_deals_total(date_from, date_to)

if numero_operaciones>0:
    print(f"Número total de operaciones en el historial: {numero_operaciones}")
else:
    print("No existen operaciones en el historial")



'''History_deals_get()'''
# Devuelve una clase TradeDeal que contiene los atributos de las operaciones en el historial de la cuenta.
# Podemos aplicar filtros opcionales para obtener solo las operaciones que cumplan con ciertos criterios
#       group: Un activo o grupo de activos. El parámetro de grupo permite múltiples condiciones separadas por comas.
#              Se pueden incluir todos los elementos con '*', excluir elementos con '!', y las condiciones se aplican en orden.

# obtenemos el historial de todas operaciones entre las fechas dadas

date_from = datetime(2023, 4, 1)
date_to = datetime(2023, 10, 1)

historial_operaciones = mt5.history_deals_get(date_from, date_to)

historial_operaciones = mt5.history_deals_get(date_from, date_to, group='NDX, ')
ingreso = historial_operaciones[0]
ingreso = historial_operaciones[0].profit

historial_operaciones = mt5.history_deals_get(date_from, date_to, group='AAPL, MSFT')

historial_operaciones = mt5.history_deals_get(date_from, date_to, group='*, !NDX')


historial_operaciones = mt5.history_deals_get(date_from, date_to, group='EURUSD')

historial_operaciones = mt5.history_deals_get(date_from, date_to, group='*EUR*')

historial_operaciones = mt5.history_deals_get(date_from, date_to, group='*, !*USD*')


historial_operaciones[15]

len(historial_operaciones)
list(set(operacion.symbol for operacion in historial_operaciones))

historial_operaciones[5].time_msc
historial_operaciones[1].symbol

historial_operaciones[0]    # Deposito de fondos
historial_operaciones[1]    # primera operación

operacion_2 = historial_operaciones[2]
simbolo_operacion_2 = operacion_2.symbol

# Convertimos el historial de operaciones en un DataFrame de pandas y tratamos los datos
historial_operaciones_df = pd.DataFrame(historial_operaciones)

historial_operaciones_df = pd.DataFrame(historial_operaciones,columns=historial_operaciones[0]._asdict().keys())

historial_operaciones_df.iloc[1]

historial_operaciones_df['time'] = pd.to_datetime(historial_operaciones_df['time'], unit='s')

historial_operaciones_df['time_msc'] = pd.to_datetime(historial_operaciones_df['time_msc'], unit='ms')

# eliminamos las filas que contengan 0 en entry y al mismo tiempo 0 en profit
historial_operaciones_df = historial_operaciones_df[~((historial_operaciones_df['entry']==0) & (historial_operaciones_df['profit']==0))]


profit =historial_operaciones_df['profit'].sum()
balance = ingreso + profit





'''history_orders_total()'''
# Devuelve el número total de movimientos de operaciones en el historial de la cuenta.'''

date_from = datetime(2023, 4, 1)    # fecha inicial en formato datetime (año, mes, día) en Etc/UTC

timezone = pytz.timezone("Etc/UTC")
date_to = datetime.now(timezone)    # fecha final en formato datetime (año, mes, día) en Etc/UTC


numero_operaciones = mt5.history_orders_total(date_from, date_to)

if numero_operaciones>0:
    print(f"Número total de ordenes en el historial: {numero_operaciones}")
else:
    print("No existen ordenes en el historial")




'''history_orders_get()'''
# Devuelve una clase TradeOrder que contiene los atributos de los movimientos de operaciónes en el historial de la cuenta.
# Podemos aplicar filtros opcionales para obtener solo las operaciones que cumplan con ciertos criterios
#       group: Un activo o grupo de activos. El parámetro de grupo permite múltiples condiciones separadas por comas. 
#              Se pueden incluir todos los elementos con '*', excluir elementos con '!', y las condiciones se aplican en orden. 


# obtenemos el historial de todas operaciones entre las fechas dadas
movimiento_operaciones = mt5.history_orders_get(date_from, date_to)

posicion_operaciones = pd.DataFrame(movimiento_operaciones)

posicion_operaciones = pd.DataFrame(movimiento_operaciones,columns=movimiento_operaciones[0]._asdict().keys())


posicion_operaciones['time_setup'] = pd.to_datetime(posicion_operaciones['time_setup'], unit='s')
posicion_operaciones['time_setup_msc'] = pd.to_datetime(posicion_operaciones['time_setup_msc'], unit='ms')
posicion_operaciones['time_done'] = pd.to_datetime(posicion_operaciones['time_done'], unit='s')
posicion_operaciones['time_done_msc'] = pd.to_datetime(posicion_operaciones['time_done_msc'], unit='ms')



# Comparamos los dos dataframes
historial_operaciones_df
posicion_operaciones



# Creamos nuestro propio DataFrame con los datos que nos interesan: 'Date_open','Date Close','Symbol','Type', 'position_id','Lot','Price_open','Price_close','profit', 'commisions', 'swap'
op_hist = historial_operaciones_df.copy()
op_hist = op_hist[['time_msc','symbol','type','position_id','volume','price','profit','commission','swap']]
# renombramos las columnas
op_hist.columns = ['Date_close','Symbol','Type', 'id','Lot','Price_close','Profit', 'commisions', 'swap']

len(op_hist)

op_pos = posicion_operaciones.copy()
op_pos = op_pos[['ticket','time_done_msc', 'price_current']]
op_pos.columns = ['id','Date_open','Price_open']

len(op_pos)

op = pd.merge(op_hist, op_pos, on='id', how='left')

len(op)

op = op.reindex(columns=['Date_close','Date_open','id','Symbol','Type','Lot','Price_open','Price_close','commisions', 'swap','Profit'])

# en los NaT de Date_open ponemos la fecha de Date_close
op['Date_open'] = op['Date_open'].fillna(op['Date_close'])

# en los NaN de Price_open ponemos el valor de Price_close
op['Price_open'] = op['Price_open'].fillna(op['Price_close'])

# miramos los valores únicos de la columna Type
op['Type'].unique()

# cambiamos los valores de Type por los que queremos
op['Type'] = op['Type'].replace({1:'Buy', 0:'Sell', 2:'Ingreso', 15:'Dividendo'})

op.head(60)

# eliminamos la columna id 
#op = op.drop('id', axis=1)

# sustituimos los valores de id por el número de operación
op['id'] = op.index 

# indexamos por Date_close
op = op.set_index('Date_close')


# creamos una columna con el beneficio por operación sumando (los valores son negativos) las comisiones y el swap
op['Profit_net'] = op['Profit'] + op['commisions'] + op['swap']

# creamos unas columnas con el beneficio acumulado y el beneficio neto acumulado
op['Profit_acum'] = op['Profit'].cumsum()
op['Profit_net_acum'] = op['Profit_net'].cumsum()

# creamos una columna con la suma de las comisiones y swap, y otra con la suma acumulada
op['Commisions+swap'] = op['commisions'] + op['swap']
op['Commisions+swap_acum'] = op['Commisions+swap'].cumsum()


# Graficamos el beneficios acumulados 
plt.figure(figsize=(20,10))
plt.plot(op['Profit_acum'])
plt.plot(op['Profit_net_acum'])
plt.xlabel('Date')
plt.ylabel('Profit')
plt.title('Profit acumulado')
plt.legend(['Profit','Profit_net'])
plt.grid()
plt.show()

# Graficamos las comisiones y swap acumulados
plt.figure(figsize=(20,10))
plt.plot(-(op['Commisions+swap_acum']))
plt.xlabel('Date')
plt.ylabel('Comisiones Pagadas')
plt.title('Comisiones y swap acumulados')
plt.grid()
plt.show()

# calculamos el porcentaje de comisiones pagadas sobre el beneficio bruto
porcentaje_comisiones = -op['Commisions+swap_acum'].iloc[-1]/op['Profit_acum'].iloc[-1]*100