#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa que obtiene la cantidad de prefijos distintos por cada monitor presente en un colector.
El colector a analizar se debe incluir en el codigo.
La informacion se almacena en un CSV.

Se debe indicar el colector del que se quiere obtener la informacion, actualmente se debe realizar cada colector
de manera individual, en un futuro se extiende a realizar de manera conjunta

IMPORTANTE: Las carpetas donde se almacenan los CSV deben ser creadas anteriormente a la prueba:
Por lo tanto la ruta deben existir los directorios de la ruta ResultadosCSV/Prefijos/DiaRCC/

@author: kevin
"""

"""-----Librerias utilizadas -----"""

import sys, re;
from os import *
import pandas as pd
import math
from time import time
import socket
import collections
from binascii import hexlify

#Fechas de inicio y fin del analisis
date_start = '20180110';
date_end = '20180110';

#Inicio la variable tiempo para comprobar cuanto tarda en realizar el analisis.
start_time = time()

#Creacion lista de RRCs
rrcs = []

#Se indica el colector o rango de colectores a analizar
#Inicialmente pensado para colectores independientemente, aunque con ligeros cambios se puede escalar a varios colectores
#Por lo que hay que indicar el colector uno a uno
#La lista de colectores validos es: [0,1,3,4,5,6,7,10,11,12,
#13,14,15,16,18,19,20,21]
#Por ejemplo range (18,19) indica que se va a analizar el colector 18
rango_rrcs_analizar = range(18,19)

#Debido al formato, los colectores menores de 10 se les anade un 0.
for contador in rango_rrcs_analizar:
	
	if contador < 10:
	
		if not contador == 2:
		
			rrcs.append("rrc0" + str(contador) + ".ripe")
			
	else:
	
		rrcs.append("rrc" + str(contador) + ".ripe")
		
# Fecha de analisis
fecha = '20180110'

#Nombres de las columnas leidas del TXT
column_names = ['RRC','AvsW','IPMonitor','ASMonitor','AnnouncedPrefix','longPrefix',\
            'IPType','ASPATH','Neighbor','COMMUNITIES'];

#Eliminacion columnas no importantes para este analisis
column_drop = ['longPrefix', 'Neighbor']
dataframe_all = pd.DataFrame([], columns=column_names)

#URL donde se encuentran el TXT
url = "/srv/agarcia/TFM-BGP/DATA_TXT/General/"

#Creacion de un DataFrame con la informacion del colector (escalable a varios colectores) 
dataframe_all = pd.DataFrame([], columns=column_names)
for rrc in rrcs:
    
    url_file = url+rrc+'_'+fecha+'.txt'
    data = pd.read_csv(url_file, sep='|',header=None, names=column_names, dtype={"Neighbor": object});
    dataframe_all = dataframe_all.append(data,ignore_index=True,sort=True)

dataframe_all = dataframe_all.drop(columns = column_drop)  

#Diccionario donde se almacena la informacion de prefijos por monitor
dicc_pref= {}

#Bucle que recorre todos los monitores existentes en el dataframe y crea una mascara para cada uno de ellos
#Obteniendo la cantidad de prefijos distintos por monitor y almacenandolo en el diccionario
for monitor in dataframe_all["IPMonitor"].unique():

    mask_monitor = dataframe_all["IPMonitor"] == monitor
    mask_AvsW = dataframe_all["AvsW"] != "W"
    mask_AvsW_2 = dataframe_all["AvsW"] != "STATE"
    df_anuncios = dataframe_all[mask_monitor & mask_AvsW & mask_AvsW_2]
    dicc_pref.update({monitor:[monitor,len(df_anuncios.AnnouncedPrefix.unique())]})
    
# Etiqueta para guardar el archivo
rrc = "_18"

#Nombre de las columnas del fichero CSV
labels1 = ["Monitor","Prefijos"]

#Se almacena la informacion del diccionario en un fichero CSV
dataframe_pref = pd.DataFrame.from_dict(dicc_pref,orient='index',columns = labels1)
dataframe_pref.to_csv("ResultadosCSV/Prefijos/DiaRCC/prefijos_" + date_start  + "-" + date_end + rrc + ".csv",index=False)

elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))
