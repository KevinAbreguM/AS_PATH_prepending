#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa que procesa las trazas BGP para obtener información relevante
para el proyecto, ademas une toda la informacion perteneciente a cada colector
en un dataframe de grandes proporciones y lo almacena en un CSV.

Se obtiene el formato: 
Colector | Tipo de Trama (A,B,W,State) | IP monitor | AS monitor | Prefijo Anunciado | Longitud de prefijo |
Tipo de IP | AS_PATH | COMMUNITIES

@author: kevin

"""

"""-----Librerias utilizadas -----"""

import sys, re;
from os import *
import pandas as pd
import numpy as np
from time import time,localtime, asctime
import socket


'''-------    FUNCIONES     -------'''
"""
get_list_files_BGP: 
	Utilizando los argumentos de colector y dia se obtienen
	todas los nombres de ficheros disponibles tanto para archivos bview como
	para updates, devolviendolos como una lista.
"""
def get_list_files_BGP(rrc,day):

    list_files_bview = [];
    list_files_update = [];

    for file in listdir('/srv/agarcia/TFM-BGP/DATA_TXT/'+rrc):

        if re.match("^updates." + day ,file):
		
            list_files_update.append(file);
			
        elif re.match("^bview." + day ,file):
		
            list_files_bview.append(file);
			
        else:
		
            print ('Error name file!');
            sys.exit();

    list_files_bview.sort();
    list_files_update.sort();

    list_files_BGP_day = [];
    list_files_BGP_day = list_files_bview + list_files_update;

    return list_files_BGP_day;

"""
create_mega_dataframe:
	Se crea un dataframe de gran cantidad de datos, uniendo toda la informacion relativa a un colector
	y a un dia, se elimina la informacion no relevante para el proyecto y se anade la longitud de prefijo 
	como parametro.
	
	Se utiliza para reducir el tiempo de procesamiento posterior.
"""
def create_mega_dataframe(list_df, Header, Header_drop):

    df_all_files = pd.DataFrame([], columns = Header)

    for df in list_df:
	
        df_split_prefix =  df['AnnouncedPrefix'].str.split("/",n = 1, expand = True);
        df.insert(6,'longPrefix', "/" + df_split_prefix[1])
        df_all_files = df_all_files.append(df, sort=True)

    df_all_files = df_all_files.drop(columns = Header_drop)

    return df_all_files;

''' type_prefix:
	Funcion que devuelve un string indicando si el prefijo es de tipo IPv4 o IPv6
'''
def type_prefix(prefix):

    prefix_split = prefix.split("/")[0]
	
    try:
	
        socket.inet_aton(prefix_split)
        IPPrefix = 'IPv4'
		
    except socket.error:
	
        IPPrefix = 'IPv6'

    return IPPrefix;

'''get_neighbors:
	Funcion que obtiene el AS vecino más proximo al monitor
	Ademas, se indica si el monitor realiza AS_PATH prepending
	o si no hay vecino.
'''
def get_neighbors(aspath, monitor):

    try:
	
        neighbor = aspath.split(" ")[1]
		
        if str(monitor) == neighbor:
		
            neighbor = "Monitor ASPATHPrep"
			
    except IndexError:
	
        neighbor = "No-Neighbor"

    return neighbor

''' add_moreinfo:
	Funcion que anade informacion adicional al dataframe con
	los siguientes atributos:
		- Colector
		- Tipo de IP del prefijo anunciado
		- AS vecino
'''
def add_moreinfo(df_all_files,rrc):

    add_ID_RRC = [];
    add_IPType = [];
    add_neighbor = [];

    for index, row in df_all_files.iterrows():

        rrc_info = rrc.split(".")[0]
        add_ID_RRC.append(rrc_info)

        ABW = row.ABW;
		
        if ABW == 'A' or ABW == 'B':
		
            IPPrefix = type_prefix(row.AnnouncedPrefix)
            add_IPType.append(IPPrefix)

            neighbor = get_neighbors(row.ASPATH, row.ASMonitor)
            add_neighbor.append(neighbor)
			
        else:
		
            add_IPType.append('-')
            add_neighbor.append('-')

    df_all_files.insert(0,'RRC_ID',add_ID_RRC)
    df_all_files.insert(4,'IPType',add_IPType)
    df_all_files.insert(5,'Neighbor',add_neighbor)

    df_day = df_all_files[['RRC_ID','ABW','IPMonitor','ASMonitor','AnnouncedPrefix',\
                            'longPrefix','IPType','ASPATH','Neighbor','COMMUNITIES']]

    return df_day;



# =================================== Main() ===================================
start_time = time()


# Lista de colectores disponibles para el dia 10-01-2018
rrcs = ['rrc00.ripe','rrc01.ripe','rrc03.ripe','rrc04.ripe','rrc05.ripe','rrc06.ripe',\
        'rrc07.ripe','rrc10.ripe','rrc11.ripe','rrc12.ripe','rrc13.ripe','rrc14.ripe',\
        'rrc15.ripe','rrc16.ripe','rrc18.ripe','rrc19.ripe','rrc20.ripe','rrc21.ripe']
day = '20180110'

#Bucle para analizar cada colector independientemente.
for rrc in rrcs:

    list_files_BGP = get_list_files_BGP(rrc,day);

	# Formato de las trazas txt antes de procesar.
    Header = ['Tipo', 'Tiempo','ABW','IPMonitor','ASMonitor','AnnouncedPrefix','ASPATH',\
            'ORIGIN','NEXTHOP','NumASPATH','ASPATHORIGEN','COMMUNITIES', '-3','-4','-5']
	# Columnas con informacion no significativa para el proyecto.
    Header_drop = ['Tipo', 'Tiempo','ORIGIN','NEXTHOP','NumASPATH',\
                    'ASPATHORIGEN', '-3','-4','-5']

    list_df = [];
	
	#Se obtiene una lista con la informacion (en forma de dataframe) de cada archivo disponible para ese colector
    for file in list_files_BGP:
	
        df = pd.read_csv('/srv/agarcia/TFM-BGP/DATA_TXT/'+rrc+'/' + file, sep='|',  \
                            header=None, names=Header);
        df = df.fillna({'COMMUNITIES':'-'})
        df = df.fillna({'ASPATH':'-'})

        list_df.append(df)

    df_all_files = create_mega_dataframe(list_df, Header, Header_drop)
    df_day = add_moreinfo(df_all_files,rrc);
	# Se almacena la informacion en la URL indicada
    df_day.to_csv(r'/srv/agarcia/TFM-BGP/DATA_TXT/General/'+rrc+'_'+day+'.txt',sep='|',header=None, index=False)


# Las trazas se encuentran en la ruta /srv/agarcia/TFM-BGP/DATA_TXT/ y se almacenan en /srv/agarcia/TFM-BGP/DATA_TXT/General/