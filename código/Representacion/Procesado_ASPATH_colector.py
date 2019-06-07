#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel AS_PATH. 
Se realiza distintas funciones/agrupaciones para obtener resultados individuales de cada colector y 
mostrar la tendencia tipica.

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/ASPATH_imagenes/DiaRCC/", ya que es donde se almacenan las imagenes.

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

'''-------    FUNCIONES     -------'''


'''representacion_1_figura_cantidad_prefijos:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
	La figura esta compuesta por distintos elementos de tipo plot
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_cantidad_prefijos(lista,labels,fechas,tamano,ylabel,xlabel,title,num_imagen,fecha,url):
    
	#Se divide la lista en distintas listas, una para cada parametro
    lista_porcentaje_0 = []
    lista_porcentaje_1 = []
    lista_porcentaje_2 = []
    lista_porcentaje_3 = []
    lista_porcentaje_4 = []
    lista_porcentaje_5 = []

    for x in lista:
	
        lista_porcentaje_0.append(x[0])
        lista_porcentaje_1.append(x[1])
        lista_porcentaje_2.append(x[2])
        lista_porcentaje_3.append(x[3])
        lista_porcentaje_4.append(x[4])
        lista_porcentaje_5.append(x[5])

	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)
	
	#Anado elementos a la figura de tipo plot
    rects1 = ax.plot(fechas,lista_porcentaje_0,color = 'b',label = labels[0])
    rects1 = ax.plot(fechas,lista_porcentaje_1,color = 'g',label = labels[1])
    rects1 = ax.plot(fechas,lista_porcentaje_2,color = 'r',label = labels[2])
    rects1 = ax.plot(fechas,lista_porcentaje_3,color = 'c',label = labels[3])
    rects1 = ax.plot(fechas,lista_porcentaje_4,color = 'm',label = labels[4])
    rects1 = ax.plot(fechas,lista_porcentaje_5,color = 'y',label = labels[5])

	#Anado informacion sobre la grafica y los ejes
    ax.set_ylim(0,1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
	
    #almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''representacion_1_figura_lista:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
	La figura esta compuesta por distintos elementos de tipo plot
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_lista(fechas,fechas2,fechas3,lista,label1,label2,label3,tamano,ylabel,xlabel,title,num_imagen,fecha,url):

	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

	#Anado elementos a la figura de tipo plot
    rects1 = ax.plot(lista,fechas,color = 'b',label = label1)
    rects1 = ax.plot(lista,fechas2,color = 'r',label = label2)
    rects1 = ax.plot(lista,fechas3,color = "y",label=label3)

	#Anado informacion sobre la grafica y los ejes
    ax.set_ylim(0,1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
    
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''informacion_ip:
	Funcion que obtiene si el AS_PATH ha sido utilizado para enviar
	anuncios de prefijos IPv4, IPv6 o para ambos tipos.
	Se devuelve la cantidad de AS_PATHs de cada grupo
'''
def informacion_ip(data):
    
	#Obtencion de la longitud total de AS_PATHs
    aspath_totales = len(data)
	
	#Aplico distintas mascaras en funcion del tipo de IP (o ambos)
    mask_ipv4 = data["IPv4"] > 0
    mask_ipv4_n = data["IPv4"] == 0
    mask_ipv6 = data["IPv6"] > 0
    mask_ipv6_n = data["IPv6"] == 0

    data_ipv4 = data[mask_ipv4 & mask_ipv6_n]
    data_ipv6 = data[mask_ipv6 & mask_ipv4_n]
    data_ip = data[mask_ipv4 & mask_ipv6]

	#Obtencion de la longitud total de cada tipo de IP (o ambos)
    aspath_ipv4 = len(data_ipv4)
    aspath_ipv6 = len(data_ipv6)
    aspath_ip = len(data_ip)

    return [aspath_ipv4,aspath_ipv6,aspath_ip,aspath_totales]

'''informacion_cantidad_prefijos_anunciados:
	Funcion que procesa la cantidad de prefijos anunciados agrupando en distintos grupos indicados
	a traves del parametro umbral.
	Finalmente se devuelve una lista con el porcentaje de todas las categorias, separadas por los umbrales y con etiquetas
	para su identificacion
'''
def informacion_cantidad_prefijos_anunciados(data,umbral):

	#Obtencion de la columna "PrefijosAnunciados"
    lista_PrefijosAnunciados = data["PrefijosAnunciados"].tolist()
    cantidad_PrefijosAnunciados = [0]*(len(umbral)+1)
	
    cantidad_total = len(lista_PrefijosAnunciados)
	
	#Divido la lista de prefijos anunciados en las distintas categorias
    for x in lista_PrefijosAnunciados:
    
        if x < umbral[0]:
        
            cantidad_PrefijosAnunciados[0] = cantidad_PrefijosAnunciados[0]+1
        
        elif x >= umbral[0] and x < umbral[1]:
        
            cantidad_PrefijosAnunciados[1] = cantidad_PrefijosAnunciados[1]+1
        
        elif x >= umbral[1] and x < umbral[2]:
        
            cantidad_PrefijosAnunciados[2] = cantidad_PrefijosAnunciados[2]+1
        
        elif x >= umbral[2] and x <= umbral[3]:
        
            cantidad_PrefijosAnunciados[3] = cantidad_PrefijosAnunciados[3]+1
        
        elif x > umbral[3] and x <= umbral[4]:
        
            cantidad_PrefijosAnunciados[4] = cantidad_PrefijosAnunciados[4]+1
        
        else: 
        
            cantidad_PrefijosAnunciados[5] = cantidad_PrefijosAnunciados[5]+1
        
    porcentajes_PrefijosAnunciados = [0]*(len(umbral)+1)
    contador = 0
    
	#Obtencion del porcentaje de cada categoria
    for x in cantidad_PrefijosAnunciados:
        
        porcentajes_PrefijosAnunciados[contador] = x/cantidad_total
        contador = contador + 1
		
	#Anado el nombre de cada categoria
    labels = [str(umbral[0]-1) + " Prefijo",str(umbral[0]) + " a " + str(umbral[1]-1) + " Prefijos",
              str(umbral[1]) + " a " + str(umbral[2]-1) + " Prefijos",str(umbral[2]) + " a " + str(umbral[3]-1) + " Prefijos",
              str(umbral[3]) + " a " + str(umbral[4]-1) + " Prefijos","Mas de " + str(umbral[4]) + " Prefijos"]
			  
    return [porcentajes_PrefijosAnunciados,labels]

'''representacion_1_figura_lista_prep:
	Funcion que representa una figura a partir de dos listas que se pasan por parametro.
	La figura esta compuesta por distintos elementos de tipo plot
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_lista_prep(lista1,lista2,fechas,labels,tamano,ylabel,xlabel,title,num_imagen,fecha,url):

	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

	#Anado elementos a la figura de tipo plot
    rects1 = ax.plot(fechas,lista1,color = 'b',label = labels[0])
    rects1 = ax.plot(fechas,lista2,color = 'c',label = labels[1])

	#Anado informacion sobre la grafica y los ejes
    ax.set_ylim(0,1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
    
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''representacion_1_figura_numASes_prep:
	Funcion que representa una figura a partir del numero de ASes que realizan AS_PATH
	prepending por AS_PATH (se pasa por argumento como lista), 
	dividiendo en 6 categorias (1,2,3,4,5 o mas) ASes
'''
def representacion_1_figura_numASes_prep(lista1,fechas,tamano,ylabel,xlabel,title,num_imagen,url,fecha):

    lista_contador = []
    
	#Divido la lista en las 6 agrupaciones disponibles
    for x in lista1:
	
        lista_total =  [0]*6
		
        for z in x:
		
            if z == 1:
			
                lista_total[0] = lista_total[0]+1
				
            elif z == 2:
			
                lista_total[1] = lista_total[1] + 1
				
            elif z == 3:
			
                lista_total[2] = lista_total[2] + 1
				
            elif z == 4:
			
                lista_total[3] = lista_total[3] + 1
				
            elif z == 5:
			
                lista_total[4] = lista_total[4] + 1
				
            else:
			
                lista_total[5] = lista_total[5] + 1
    
        lista_contador.append(lista_total)
	
	#Obtengo el porcentaje de cada agrupacion
    lista_porcentaje_1 = []
    lista_porcentaje_2 = []
    lista_porcentaje_3 = []
    lista_porcentaje_4 = []
    lista_porcentaje_5 = []
    lista_porcentaje_6 = []

    for x in lista_contador:
	
        longitud_total = sum(x)
        lista_contador_porc =  [0]*6
        
        for contador in range(0,6):
		
            if x[contador] != 0:
			
                lista_contador_porc[contador] = x[contador]/longitud_total
				
            else:
			
                lista_contador_porc[contador] = 0
				
        lista_porcentaje_1.append(lista_contador_porc[0]) 
        lista_porcentaje_2.append(lista_contador_porc[1]) 
        lista_porcentaje_3.append(lista_contador_porc[2]) 
        lista_porcentaje_4.append(lista_contador_porc[3]) 
        lista_porcentaje_5.append(lista_contador_porc[4]) 
        lista_porcentaje_6.append(lista_contador_porc[5]) 

    #Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

    labels = ["1 AS prepending","2 ASes prepending","3 ASes prepending","4 ASes prepending","5 ASes prepending","mas de 5 ASes prepending"]
	
	#Anado elementos a la figura de tipo plot
    rects1 = ax.plot(fechas,lista_porcentaje_1,color = 'b',label = labels[0])
    rects1 = ax.plot(fechas,lista_porcentaje_2,color = 'g',label = labels[1])
    rects1 = ax.plot(fechas,lista_porcentaje_3,color = 'r',label = labels[2])
    rects1 = ax.plot(fechas,lista_porcentaje_4,color = 'c',label = labels[3])
    rects1 = ax.plot(fechas,lista_porcentaje_5,color = 'm',label = labels[4])
    rects1 = ax.plot(fechas,lista_porcentaje_6,color = 'y',label = labels[5])

	#Anado informacion sobre la grafica y los ejes
    ax.set_ylim(0,1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
    
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''-------    main     -------'''

#Variables para la representacion de imagenes
num_imagen = 1

start_time = time()

#URLs donde se encuentran los ficheros CSV
url = "ResultadosCSV/ASPATH/DiaRCC/ASPATH_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/ASPATH_imagenes/DiaRCC/ASPATH_global_"

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]
fecha_inicio = rrc[0]

data_aspath = []

#Se crea una lista con informacion de cada colector independientemente
for urls in rrc:
    data_aspath.append(pd.read_csv(url+"20180110-20180110"+urls+".csv",sep=","))

#Variables para la representacion
lista_ip_porcentajes_ambos = []
lista_ip_porcentajes_ipv4 = []
lista_ip_porcentajes_ipv6 = []

lista_cantidad_prefAnunciados = []

lista_no_prep = []
lista_prep=[]
lista_numprep = []

#Recorro cada dataframe de cada colector y obtengo la informacion a representar
for data in data_aspath:

	#Distribucion IP del AS_PATH
    [aspath_ipv4,aspath_ipv6,aspath_ip,aspath_totales] = informacion_ip(data)
	
	#Porcentajes de IPv4, IPv6 o ambos
    lista_ip_porcentajes_ambos.append(aspath_ip/aspath_totales)
    lista_ip_porcentajes_ipv4.append(aspath_ipv4/aspath_totales)
    lista_ip_porcentajes_ipv6.append(aspath_ipv6/aspath_totales)
    
	#Distribucion de prefijos distintos anunciados por AS_PATH
    [cantidad_PrefijosAnunciados,lista_labels_PrefijosAnunciados] = informacion_cantidad_prefijos_anunciados(data
    ,[2,5,20,100,1000])
    lista_cantidad_prefAnunciados.append(cantidad_PrefijosAnunciados)
    
	#Distribucion de AS_PATH sobre los que se observa AS_PATH prepending
    num_aspath_prepending = data["Prepending"].sum()
    num_aspath_no_prepending =  aspath_totales-num_aspath_prepending
    
    lista_no_prep.append(num_aspath_no_prepending/aspath_totales)
    lista_prep.append(num_aspath_prepending/aspath_totales)
    
	#Distribucion numero ASes que realiza AS_PATH prepending por AS_PATH
    mask_prepending = data["Prepending"] > 0
    data_prepending = data[mask_prepending]
    lista_numprep.append(data_prepending["Num_ASesPrepending"].tolist())

#Representaciones de distribucion IP - Cantidad de prefijos distintos anunciados -
#Si se observa AS_PATH prepending o no en el AS_PATH  - Numero de ASes que realizan AS_PATH prepending
#por AS_PATH
title = ""
num_imagen = representacion_1_figura_lista(lista_ip_porcentajes_ambos,lista_ip_porcentajes_ipv4,lista_ip_porcentajes_ipv6,rrc,
                                           "aspaths con prefijos de ambos tipos IP","aspaths con prefijos IPv4","aspaths con prefijos IPv6",(10,5),"Porcentaje","RRC",title,num_imagen,fecha_inicio,url_imagen)

title = ""
num_imagen = representacion_1_figura_cantidad_prefijos(lista_cantidad_prefAnunciados,lista_labels_PrefijosAnunciados,rrc,(10,5),
                    "Porcentaje","RRC",title,num_imagen,fecha_inicio,url_imagen)

labels_prep = ["aspaths con prepending", "aspaths sin prepending"]
title = ""
num_imagen = representacion_1_figura_lista_prep(lista_no_prep,lista_prep,rrc,labels_prep,(10,5),"Porcentaje",
                "RRC",title,num_imagen,fecha_inicio,url_imagen)

title = ""
num_imagen = representacion_1_figura_numASes_prep(lista_numprep,rrc,(10,5),"Porcentaje","RRC",title,num_imagen,url_imagen,fecha_inicio)
print("ok")