#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel de prefijos mas AS vecinos y 
realiza distintas funciones/agrupaciones para obtener distintas representaciones a este nivel

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
import random
from time import time

'''-------    FUNCIONES     -------'''

'''func:
	Funcion auxiliar utilizada para parametros de la funcion representacion pie
'''
def func(pct,allvals,nombre):

    absolute = int(pct/100.*np.sum(allvals))
    prueba = "{:.2f}%\n({:d} " + nombre+ " ) "
    return prueba.format(pct,absolute)
	
'''diccionarios_informacion:
	Funcion que obtiene informacion del monitor a nivel de entradas BGP y de pares (prefijos + AS vecino)
	y se obtiene porcentajes de realizacion de AS_PATH prepending para cada caso.
	Se obtiene:
		- Lista con la cantidad de entradas BGP que realizan AS_PATH prepending
		- Lista con la cantidad de entradas BGP totales
		- Diccionario con el porcentaje de AS_PATH prepending a nivel Entradas BGP por monitor
		- Lista con la cantidad de pares (prefijo + vecino) que realizan AS_PATH prepending
		- Lista con la cantidad de pares (prefijo + vecino) totales
		- Diccionario con el porcentaje de AS_PATH prepending a nivel par (prefijo + vecino) por monitor
		- Lista con la cantidad de pares que realizan siempre AS_PATH prepending
		- Diccionario con el porcentaj de la cantidad de pares que realizan siempre AS_PATH prepending sobre el total de pares que realizan AS_PATH prepending

	
'''
def diccionarios_informacion(monitor,data_IP,lista_prepending_monitor, lista_total_monitor,dicc_porcentaje_monitor,
            lista_prepending_monitor_unico,lista_total_monitor_unico,dicc_porcentaje_monitor_unico,
            lista_prepending_igual_total,dicc_porcentaje_prepending_igual_total):
    
	#Se optiene la cantidad de entradas BGP totales y que se realiza AS_PATH prepending por DF monitor
    prepending_monitor = data_IP.Prepending.sum()
    total_monitor = data_IP.totales.sum()
	
	#Porcentaje de realizacion de AS_PATH prepending a nivel entradas BGP
    porcentaje_monitor = prepending_monitor / total_monitor

    lista_prepending_monitor.append(prepending_monitor)
    lista_total_monitor.append(total_monitor)
    dicc_porcentaje_monitor.update({monitor:porcentaje_monitor})

    #Se crea y aplica mascara de AS_PATH prepending
    mask2 = data_IP["Prepending"] > 0
    data_monitor_prepending = data_IP[mask2]

	#Numero del par prefijo + AS vecino que realiza AS_PATH prepending
    prepending_monitor_unico = len(data_monitor_prepending)
    total_monitor_unico = len(data_IP)
	
    #Porcentaje de realizacion de AS_PATH prepending a nivel par prefijo + vecino
    if prepending_monitor_unico == 0:
	
        porcentaje_monitor_unico = 0
		
    else:
	
        porcentaje_monitor_unico = prepending_monitor_unico/total_monitor_unico

    
    lista_prepending_monitor_unico.append(prepending_monitor_unico)
    lista_total_monitor_unico.append(total_monitor_unico)
    dicc_porcentaje_monitor_unico.update({monitor:porcentaje_monitor_unico})

    #Obtencion de si cuando se realiza AS_PATH prepending, el par prefijo + vecino lo realiza siempre o solo ocasionalmente
    C = np.where((data_monitor_prepending["Prepending"] ==
                                         data_monitor_prepending["totales"]),1,0)
    prepending_igual_totales = C.sum()
	
	#Porcentaje de pares (prefijo + vecino) que realizan AS_path prepending siempre 
    porcentaje_prepending_igual_totales = prepending_igual_totales/prepending_monitor_unico
   
    
    lista_prepending_igual_total.append(prepending_igual_totales)
    dicc_porcentaje_prepending_igual_total.update({monitor:porcentaje_prepending_igual_totales})
    
    
    return [lista_prepending_monitor, lista_total_monitor,dicc_porcentaje_monitor,
            lista_prepending_monitor_unico,lista_total_monitor_unico,dicc_porcentaje_monitor_unico,
            lista_prepending_igual_total,dicc_porcentaje_prepending_igual_total]



'''representacion_pie:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
	La figura es un diagrama de circular.
	Se establece parametros para caracterizar la figura, incluyendo la leyenda.
	La figura se almacena en la URL indicada
'''
def representacion_pie(tamano,lista,labels,title_leyenda,title,num_imagen,fecha,url_imagen,nombre):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(figsize = tamano,subplot_kw = dict(aspect="equal"))

	#Plot de tipo diagrama circular con los elementos de la lista
    wedges,texts,autotexts = ax.pie(lista,autopct=lambda pct: func(pct,lista,nombre),textprops=dict(color="w"))
	
	# Se anade caracteristicas de la leyenda, texto y titulo
    ax.legend(wedges,labels,title = title_leyenda,loc = "center left", bbox_to_anchor = (1,0,0.5,1))
    plt.setp(autotexts,size=8,weight="bold")
    ax.set_title(title,fontsize=12,fontweight='bold')
    
	#almaceno la figura en la url indicada
    savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")
    num_imagen = num_imagen + 1
    
    return num_imagen

'''diccionario_prefijos_validos:
	Funcion que devuelve un diccionario con la cantidad de pares prefijos + vecinos distintos por cada monitor 
	presente en el DataFrame
'''
def diccionario_prefijos_validos(data):
    
	#Se recorre el DataFrame con todos los monitores existentes
    lista_monitores = data.ASMonitor.unique().tolist()
    diccionario_monitores_prefijos_validos = {}
    diccionario_monitores_prefijos_validos_ipv6 = {}

    for monitor in lista_monitores:
		
		#Creacion y aplicacion de mascara del monitor
        mask_monitor = data["ASMonitor"] == monitor
        df_monitor = data[mask_monitor]
		
		#Se almacena separando por tipo de IP del monitor
        try:
            
            socket.inet_aton(monitor)
			
            diccionario_monitores_prefijos_validos.update({monitor: len(df_monitor)})
            
        except socket.error:
		
            diccionario_monitores_prefijos_validos_ipv6.update({monitor: len(df_monitor)})

    return [diccionario_monitores_prefijos_validos,diccionario_monitores_prefijos_validos_ipv6]
    

'''representacion_1_figura_lista_ordenada:
	Funcion que representa una figura a partir de una lista ordenada que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_lista_ordenada(lista,tamano,bar_width,opacity,
                                        ylabel,xlabel,title,num_imagen,fecha,url,tipo_ip):
    
    
    #Dependiendo del tipo de IP se elige el color de la gráfica
    if tipo_ip == "IPv4":
	
        color1 = "b"
		
    else:
	
        color1 = "y"

	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

    n_groups = len(lista)
    index = np.arange(n_groups)
	
	#Plot de tipo bar con los elementos de la lista
    ax.plot(lista,color = "r")
    rects1 = ax.bar(index,lista,bar_width,alpha = opacity,color=color1)

	#Anado informacion sobre la grafica
    ax.set_xticks([],[])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    
	#Almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
    num_imagen = num_imagen + 1

    return num_imagen




'''eliminar_valor_lista_alto:
	Funcion que devuelve una lista identica a la pasada por parametro, pero eliminando valores que superan una condicion
'''
def eliminar_valor_lista_alto(lista,condicion):

    lista_aux = []
	
    for x in lista:
	
        if x < condicion:
		
            lista_aux.append(x)
			
    return lista_aux


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
url = "ResultadosCSV/Prefijos_Vecinos/DiaRCC/Monitor_Prefijo_Vecino_"

#Variable utilizada para almacenar la imagen
num_imagen = 1

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/Prefijos_Vecinos_imagenes/DiaRCC/Monitor_Prefijo_Vecino_"

#Se agrupa todos los datos de los distintos CSV en un unico dataframe
contador = 0
for version_rrc in rrc:

    if contador == 0:
	
        data = pd.read_csv(url+fecha+version_rrc+".csv",sep=",")
        contador = 1
		
    else:
	
        data = data.append(pd.read_csv(url+fecha+version_rrc+".csv",sep=","),ignore_index = True)
		
#Se elimina columna innecesaria del dataframe
del data["Unnamed: 0"]

print("Ya uní todos los dataframes")
elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))

#Obtengo la cantidad del par prefijos + AS vecino por cada monitor
[diccionario_monitores_prefijos_validos,
            diccionario_monitores_prefijos_validos_ipv6] = diccionario_prefijos_validos(data)

#Obtengo lista ordenada con la cantidad de prefijos por cada monitor
lista_ordenada_monitores_prefijos_validos_ipv4 = list(diccionario_monitores_prefijos_validos.values())
lista_ordenada_monitores_prefijos_validos_ipv4.sort()

lista_ordenada_monitores_prefijos_validos_ipv6 = list(diccionario_monitores_prefijos_validos_ipv6.values())
lista_ordenada_monitores_prefijos_validos_ipv6.sort()

#Representacion de la cantidad de pares prefijos + AS vecinos distintos por monitor
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_monitores_prefijos_validos_ipv4,(10,5),bar_width,opacity,
                                        "Número par Prefijos + Vecinos distintos","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")


lista_ordenada_monitores_prefijos_validos_ipv6 = eliminar_valor_lista_alto(lista_ordenada_monitores_prefijos_validos_ipv6,300000)
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_monitores_prefijos_validos_ipv6,(10,5),bar_width,opacity,
                                        "Número par Prefijos + Vecinos distintos","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")


lista_monitores = data.ASMonitor.unique().tolist()


#variables para obtener estadisticas de realizacion de AS_PATH prepending a nivel de entradas BGP y 
# a nivel de pares (prefijos + AS vecinos)
lista_prepending_monitor = []
lista_total_monitor = []
dicc_porcentaje_monitor = {}
lista_prepending_monitor_unico = []
lista_total_monitor_unico = []
dicc_porcentaje_monitor_unico = {}
lista_prepending_igual_total = []
dicc_porcentaje_prepending_igual_total = {}

lista_prepending_monitor_ipv6 = []
lista_total_monitor_ipv6 = []
dicc_porcentaje_monitor_ipv6 = {}
lista_prepending_monitor_unico_ipv6 = []
lista_total_monitor_unico_ipv6 = []
dicc_porcentaje_monitor_unico_ipv6 = {}
lista_prepending_igual_total_ipv6 = []
dicc_porcentaje_prepending_igual_total_ipv6 = {}

#Bucle para obtener las estadisticas de AS_PATH prepending por cada monitor
for monitor in lista_monitores:
    
    mask = data["ASMonitor"] == monitor
    data_monitor = data[mask]
	
    try:
	
        socket.inet_aton(monitor)
        [lista_prepending_monitor, lista_total_monitor,dicc_porcentaje_monitor,lista_prepending_monitor_unico,
         lista_total_monitor_unico,dicc_porcentaje_monitor_unico,lista_prepending_igual_total,dicc_porcentaje_prepending_igual_total
         ] = diccionarios_informacion(monitor,data_monitor,lista_prepending_monitor, lista_total_monitor,dicc_porcentaje_monitor,
            lista_prepending_monitor_unico,lista_total_monitor_unico,dicc_porcentaje_monitor_unico,
            lista_prepending_igual_total,dicc_porcentaje_prepending_igual_total)
			
    except socket.error:    
	
        [lista_prepending_monitor_ipv6, lista_total_monitor_ipv6,dicc_porcentaje_monitor_ipv6,lista_prepending_monitor_unico_ipv6,
         lista_total_monitor_unico_ipv6,dicc_porcentaje_monitor_unico_ipv6,lista_prepending_igual_total_ipv6,dicc_porcentaje_prepending_igual_total_ipv6
         ] = diccionarios_informacion(monitor,data_monitor,lista_prepending_monitor_ipv6, lista_total_monitor_ipv6,dicc_porcentaje_monitor_ipv6,
            lista_prepending_monitor_unico_ipv6,lista_total_monitor_unico_ipv6,dicc_porcentaje_monitor_unico_ipv6,
            lista_prepending_igual_total_ipv6,dicc_porcentaje_prepending_igual_total_ipv6)


#Lista con porcentaje de AS_PATH prepending a nivel de entradas BGP
lista_ordenada_porc_monitores_prefijos_validos_ipv4 = list(dicc_porcentaje_monitor.values())
lista_ordenada_porc_monitores_prefijos_validos_ipv4.sort()

lista_ordenada_porc_monitores_prefijos_validos_ipv6 = list(dicc_porcentaje_monitor_ipv6.values())
lista_ordenada_porc_monitores_prefijos_validos_ipv6.sort()

#Representacion del porcentaje de AS_PATH prepending a nivel Entradas BGP
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_prefijos_validos_ipv4,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_prefijos_validos_ipv4,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Lista con porcentaje de AS_PATH prepending a nivel del par Prefijos + AS vecino
lista_ordenada_porc_monitores_prefijos_unicos_validos_ipv4 = list(dicc_porcentaje_monitor_unico.values())
lista_ordenada_porc_monitores_prefijos_unicos_validos_ipv4.sort()

lista_ordenada_porc_monitores_unicos_prefijos_validos_ipv6 = list(dicc_porcentaje_monitor_unico_ipv6.values())
lista_ordenada_porc_monitores_unicos_prefijos_validos_ipv6.sort()

#Representacion del porcentaje de AS_PATH prepending a nivel del par Prefijos + AS vecino
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_prefijos_unicos_validos_ipv4,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_unicos_prefijos_validos_ipv6,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Lista con porcentaje de pares prefijos + AS vecino sobre el que siempre se realiza AS_PATH prepending
lista_ordenada_porc_monitores_igual_total_validos_ipv4 = list(dicc_porcentaje_prepending_igual_total.values())
lista_ordenada_porc_monitores_igual_total_validos_ipv4.sort()

lista_ordenada_porc_monitores_igual_total_validos_ipv6 = list(dicc_porcentaje_prepending_igual_total_ipv6.values())
lista_ordenada_porc_monitores_igual_total_validos_ipv6.sort()

#Representacion del porcentaje de pares prefijos + AS vecino sobre el que siempre se realiza AS_PATH prepending
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_igual_total_validos_ipv4,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_porc_monitores_igual_total_validos_ipv6,(10,5),bar_width,opacity,
                                        "Porcentajes","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")


#Representacion de entradas BGP segun realizacion de AS_PATH prepending
lista_pie = [sum(lista_prepending_monitor), sum(lista_total_monitor)-sum(lista_prepending_monitor)]
labels_pie = ["Anuncios BGP IPv4 con prepending", "Anuncios BGP IPv4 prepending"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Anuncios BGP")

lista_pie = [sum(lista_prepending_monitor_ipv6), sum(lista_total_monitor_ipv6)-sum(lista_prepending_monitor_ipv6)]
labels_pie = ["Anuncios BGP IPv6 con prepending", "Anuncios BGP IPv6 prepending"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Anuncios BGP")

#Representacion de pares prefijos + vecinos segun realización de AS_PATH prepending
lista_pie = [sum(lista_prepending_monitor_unico), sum(lista_total_monitor_unico)-sum(lista_prepending_monitor_unico)]
labels_pie = ["Par prefijo + vecino con prepending", "Par prefijo + vecino sin prepending"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Prefijo+Vecino")

lista_pie = [sum(lista_prepending_monitor_unico_ipv6), sum(lista_total_monitor_unico_ipv6)-sum(lista_prepending_monitor_unico_ipv6)]
labels_pie = ["Par prefijo + vecino con prepending", "Par prefijo + vecino sin prepending"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Prefijo+Vecino")

#Representacion del porcentaje de Pares prefijos + vecinos que realizan AS_PATH prepending siempre vs ocasionalmente
lista_pie = [sum(lista_prepending_igual_total), sum(lista_prepending_monitor_unico)-sum(lista_prepending_igual_total)]
labels_pie = ["Par prefijo + vecino siempre se observa prepending", "Par prefijo + vecino prepending a veces"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Prefijo+Vecino")

lista_pie = [sum(lista_prepending_igual_total_ipv6), sum(lista_prepending_monitor_unico_ipv6)-sum(lista_prepending_igual_total_ipv6)]
labels_pie = ["Par prefijo + vecino siempre se observa prepending", "Par prefijo + vecino prepending a veces"]
title = ""
num_imagen = representacion_pie((15,9),lista_pie,labels_pie,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen,"Prefijo+Vecino")

elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))

