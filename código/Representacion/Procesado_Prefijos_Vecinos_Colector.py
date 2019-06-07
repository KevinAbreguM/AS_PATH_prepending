"""

Codigo que procesa la informacion de los CSVs a nivel de prefijos mas AS vecinos y 
realiza agrupaciones/representaciones por cada colector para obtener tendencias

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/Prefijos_Vecinos_imagenes/DiaRCC/", ya que es donde se almacenan las imagenes.

@author: kevin
"""

"""-----Librerias utilizadas -----"""

import sys, re;
import pandas as pd
from os import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
import collections
import socket
from time import time


'''-------    main     -------'''

#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8

start_time = time()

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]

#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url = "ResultadosCSV/Prefijos_Vecinos/DiaRCC/Prefijo_Vecino_"

#Variable utilizada para almacenar la imagen
num_imagen = 1

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/Prefijos_Vecinos_imagenes/DiaRCC/Prefijo_Vecino_"

fecha_inicio = fecha

#Se agrupa todos los datos de los distintos CSV en una lista con el dataframe de cada colector
data = []
for urls in rrc:
    data.append(pd.read_csv(url+fecha+urls+".csv",sep=","))
    
#Variables para almacenar el porcentaje de AS_PATH prepending a nivel anuncios BGP
porcentaje_anunciosBGP_ipv4 = []
porcentaje_anunciosBGP_ipv6 = []


#Recorro un bucle con la lista de dataframes
for df in data:
    
    #Creo y aplico mascara por tipo de IP
    mask_ipv4 = df["IPv4"] > 0
    mask_ipv6 = df["IPv4"] == 0
    data_ipv4 = df[mask_ipv4]
    data_ipv6 = df[mask_ipv6]
    
    #Obtengo el porcentaje de realización de AS_PATH prepending a nivel de entradas BGP
    prepending_monitor = data_ipv4.Prepending.sum()
    total_monitor = data_ipv4.totales.sum()
    porcentaje_anunciosBGP_ipv4.append(prepending_monitor / total_monitor)
    
    prepending_monitor = data_ipv6.Prepending.sum()
    total_monitor = data_ipv6.totales.sum()
    porcentaje_anunciosBGP_ipv6.append(prepending_monitor / total_monitor)
    
    
    
#Representacion del porcentaje de realización de AS_PATH prepending a nivel de entradas BGP de cada colector
#Creo la figura de 1 fila y 2 columna del tamano indicado
fig,ax = plt.subplots(nrows = 1, ncols = 2,figsize=(20,5))

n_groups = len(porcentaje_anunciosBGP_ipv4)
index = np.arange(n_groups)

#Grafica con los elementos de la lista IPv4
rects1 = ax[0].plot(rrc,porcentaje_anunciosBGP_ipv4,
                 color='b')
ax[0].set_ylabel('Porcentaje')
ax[0].set_title("")
ax[0].set_xlabel("RRC")
ax[0].set_ylim(0,1)

#Grafica con los elementos de la lista IPv46
rects1 = ax[1].plot(rrc,porcentaje_anunciosBGP_ipv6,
                 color='y')
ax[1].set_ylabel('Porcentaje')
ax[1].set_title("")
ax[1].set_xlabel("RRC")
ax[1].set_ylim(0,1)
ax[0].grid()
ax[1].grid()

#Almaceno la figura en la url indicada
savefig(url_imagen+fecha_inicio+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1




elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))