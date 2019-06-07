#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que se desarrollará en un futuro y agrupa la informacion de los ficheros CSV para niveles ASes origen y ASes transito.
Uniendo la información de cada tipo de AS (independientemente) y eliminando la influencia del monitor y almacenandolo
en un fichero CSV para cada tipo de AS

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

Los ficheros se almacenan en la ruta "ResultadosCSV/ASes/DiaRCC/"
@author: kevin

"""

"""-----Librerias utilizadas -----"""

import sys, re;
import pandas as pd
from os import *
from pylab import *
import matplotlib.pyplot as plt
import collections
import socket
from time import time


'''-------    main     -------'''

start_time = time()

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]

#Fecha de los ficheros CSV	   
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url_origen = "ResultadosCSV/ASes/DiaRCC/ASes_origen_"
url_transito = "ResultadosCSV/ASes/DiaRCC/ASes_transito_"

#Se agrupa todos los datos de los distintos CSV en un dataframe (cada tipo de AS de manera independiente)

contador = 0
for version_rrc in rrc:

    if contador == 0:
	
        data_transito = pd.read_csv(url_transito+fecha+version_rrc+".csv",sep=",",dtype={"ASTransito": str})
        data_origen = pd.read_csv(url_origen+fecha+version_rrc+".csv",sep=",",dtype={"ASOrigen": str})
        contador = 1
		
    else:
	
        data = pd.read_csv(url_transito+fecha+version_rrc+".csv",sep=",",dtype={"ASTransito": str})
        data_transito = data_transito.append(data,ignore_index = True,sort = True)
        data_origen = data_origen.append(pd.read_csv(url_origen+fecha+version_rrc+".csv",sep=",",dtype={"ASOrigen": str}),ignore_index = True, sort = True)

elapsed_time = time() - start_time

print("Tiempo de ejecucion: " + str(elapsed_time))

#Se crea un diccionario con informacion global para ASes transito
dicc_transito_global = {}
contador = 0

for AS in data_transito.ASTransito.unique():

    mask_AS = data_transito["ASTransito"] == AS
    data_transito_aux = data_transito[mask_AS]
    prepending = data_transito_aux["Prepending"].sum()
    totales = data_transito_aux["Totales"].sum()
    dicc_transito_global.update({contador:[AS,prepending,totales]})
    contador = contador + 1

#Se crea un diccionario con informacion global para ASes origen
dicc_origen_global = {}
contador = 0
elapsed_time = time() - start_time

print("Tiempo de ejecucion: " + str(elapsed_time))

for AS in data_origen.ASOrigen.unique():

    mask_AS = data_origen["ASOrigen"] == AS
    data_origen_aux = data_origen[mask_AS]
    prepending = data_origen_aux["Prepending"].sum()
    totales = data_origen_aux["Totales"].sum()
    dicc_origen_global.update({contador:[AS,prepending,totales]})
    contador = contador + 1


#Se almacenan los diccionarios en CSVs con formato AS - Numero de veces que se realiza AS_PATH prepending - Numero de apariciones totales
labels = ["AS","Prepending","Totales"]

dataframe_transito_global = pd.DataFrame.from_dict(dicc_transito_global,orient='index',columns = labels)
dataframe_origen_global = pd.DataFrame.from_dict(dicc_origen_global,orient='index',columns = labels)
dataframe_transito_global.to_csv(url_transito + "_global_" + fecha +".csv",index=False)
dataframe_origen_global.to_csv(url_origen  + "_global_" + fecha +".csv",index=False)

elapsed_time = time() - start_time

print("Tiempo de ejecucion: " + str(elapsed_time))