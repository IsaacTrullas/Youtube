import pandas as pd
import ftplib  # protocolo de transferencia de archivos
import gzip # para descomprimir archivos
import tempfile # para crear archivos temporales
import os # para trabajar con archivos en el sistema operativo
import datetime as dt # para trabajar con fechas
import tqdm # para mostrar una barra de progreso
import time # para medir el tiempo de ejecución

# Credenciales de acceso al ftp
user = 'IsaacTrullas'
password = 's5iQxuATjHdOy5'
server = 'tickdata.darwinex.com'
port = 21

# Ticker de descarga
ticker = 'NDXm'

# Descargamos todos los ficheros que se encuentren en el directorio 'ticker' del servidor ftp de Darwinex
# Si no existe el directorio (ticker) lanzamos un mensaje de error

start_time = time.time() # tiempo de inicio de la descarga

with ftplib.FTP(server, user, password) as ftp:
    try:
        ftp.cwd(ticker)
    except:
        print('El ticker no existe')
        # desconectamos del servidor y salimos del programa
        ftp.quit()
        exit()
    else:
        files = ftp.nlst()
        # Filtramos los archivos para excluir '.' y '..'
        files = [file for file in files if file not in ['.', '..']]

        if files == []:
            print('No hay archivos en el directorio')
            # desconectamos del servidor y salimos del programa
            ftp.quit()
            exit()
        else:
            # Creamos un directorio temporal para almacenar los archivos descargados
            temp_dir = tempfile.TemporaryDirectory(prefix="darwinex_ticks_")
            # Descargamos los archivos en el directorio temporal
            with tqdm.tqdm(total=len(files), desc="Descargando archivos", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
                for file in files:
                    ftp.retrbinary(f'RETR {file}', open(os.path.join(temp_dir.name, file), 'wb').write, 8192)
                    pbar.update()            
            # desconectamos del servidor
            ftp.quit()

end_time = time.time() # tiempo de fin de la descarga
tiempo_descarga = end_time - start_time # tiempo de descarga
# pasamos el tiempo a horas, minutos, segundos y milisegundos
tiempo_descarga = dt.timedelta(seconds=tiempo_descarga)
print(f'Tiempo de descarga: {tiempo_descarga}')



# Creamos dos csv con los datos de BID y ASK ya descomprimidos

# Listar todos los archivos .gz en el directorio temporal
gz_files = [f for f in os.listdir(temp_dir.name) if f.endswith('.gz')]

# Inicializar el contador de tiempo
start_time = time.time()

# Crear un directorio para guardar los archivos .csv descomprimidos
csv_dir = os.path.join(temp_dir.name, 'csv_files')
os.makedirs(csv_dir, exist_ok=True)

# Crear una barra de progreso para todo el proceso
with tqdm.tqdm(total=len(gz_files), desc="Descomprimiendo y uniendo archivos", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
    
    # Primero procesar todos los archivos 'BID'
    with open(os.path.join(csv_dir, 'bid.csv'), 'w') as f_out_bid:
        for gz_file in [f for f in gz_files if 'BID' in f]:
            # Descomprimir el archivo
            with gzip.open(os.path.join(temp_dir.name, gz_file), 'rt') as f_in:
                f_out_bid.write(f_in.read())
            pbar.update()

    # Luego procesar todos los archivos 'ASK'
    with open(os.path.join(csv_dir, 'ask.csv'), 'w') as f_out_ask:
        for gz_file in [f for f in gz_files if 'ASK' in f]:
            # Descomprimir el archivo
            with gzip.open(os.path.join(temp_dir.name, gz_file), 'rt') as f_in:
                f_out_ask.write(f_in.read())
            pbar.update()

# Calcular el tiempo transcurrido
elapsed_time = time.time() - start_time
# Pasamos el tiempo a horas, minutos, segundos y milisegundos
elapsed_time = dt.timedelta(seconds=elapsed_time)

print(f"La unión de los datos ha tardado: {elapsed_time}")





# inicializamos el contador de tiempo
start_time = time.time()

# Creamos un DataFrame con todos los datos de ticks
historico = pd.DataFrame()

# Leer los archivos csv
historico = pd.merge(pd.read_csv(os.path.join(csv_dir, 'bid.csv'), names=['Date', 'Bid', 'volume_bid']), 
                     pd.read_csv(os.path.join(csv_dir, 'ask.csv'), names=['Date', 'Ask', 'volume_ask']), on='Date', how='outer')

historico = historico.dropna()


# Crear la columna 'volume' que es la suma de 'volume_bid' y 'volume_ask'
historico['Volume'] = historico['volume_bid'] + historico['volume_ask']

# Eliminar las columnas 'volume_bid' y 'volume_ask'
historico = historico.drop(['volume_bid', 'volume_ask'], axis=1)

# Ordenar el dataframe por la columna 'date'
historico = historico.sort_values('Date')
historico['Date'] = pd.to_datetime(historico['Date'], unit='ms')

# indexar el dataframe por la columna 'Date'
historico = historico.set_index('Date')

# Calcular el tiempo transcurrido
elapsed_time = time.time() - start_time
# Pasamos el tiempo a horas, minutos, segundos y milisegundos
elapsed_time = dt.timedelta(seconds=elapsed_time)

print(f"La creación del dataframe ha tardado: {elapsed_time}")

# Guardamos el dataframe 
historico.to_csv(f'{ticker}_historico_ticks.csv')


# Eliminamos el directorio temporal
temp_dir.cleanup()


# cargamos el dataframe 
historico = pd.read_csv(f'{ticker}_historico_ticks.csv', index_col='Date', parse_dates=True)




# Resample a H1 (1 houra) OHLCV
historico_resampled_h1 = historico.resample('H').agg({'Bid': ['first', 'max', 'min', 'last'], 'Volume': 'sum'})

# Aplanar nombres de columnass
historico_resampled_h1.columns = ['_'.join(col) for col in historico_resampled_h1.columns.values]

# Renombrar el nombre de las columnas a nombres OHLCV estándar
historico_resampled_h1.rename(columns={'Bid_first': 'Open', 'Bid_max': 'High', 'Bid_min': 'Low', 'Bid_last': 'Close', 'Volume_sum': 'Volume'}, inplace=True)

# Resample a D1 (1 day) OHLCV
historico_resampled_d1 = historico_resampled_h1.resample('D').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})


# Guardamos los dataframes
historico_resampled_h1.to_csv(f'{ticker}_historico_ticks_resampled_h1.csv')
historico_resampled_d1.to_csv(f'{ticker}_historico_ticks_resampled_d1.csv')