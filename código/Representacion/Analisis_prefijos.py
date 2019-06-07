#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa que representa informacion relacionada con la cantidad de prefijos distintos por tipo de monitor
Tambien se representa la distribucion por tipo de monitor (proveedores o peers/clientes)

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_informacion_prefijos" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/Prefijos_imagenes/", ya que es donde se almacenan las imagenes.
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

'''
func:
	Funcion auxiliar utilizada para parametros de la funcion representacion pie
'''
def func(pct,allvals,nombre):
    absolute = int(pct/100.*np.sum(allvals))
    prueba = "{:.2f}%\n({:d} " + nombre+ " ) "
    return prueba.format(pct,absolute)

'''
representacion_pie:
	Funcion que representa la informacion en formato de diagrama circular y
	almacena la gráfica en un directorio.
'''
def representacion_pie(tamano,lista,labels,title_leyenda,title,num_imagen,fecha,url_imagen,nombre):
    
	# Se crea la figura y se anaden caracteristicas
    fig,ax = plt.subplots(figsize = tamano,subplot_kw = dict(aspect="equal"))
    wedges,texts,autotexts = ax.pie(lista,autopct=lambda pct: func(pct,lista,nombre),textprops=dict(color="w"))
	
	# Se anade la leyenda con caracteristicas de posicion/tamano
    ax.legend(wedges,labels,title = title_leyenda,loc = "center left", bbox_to_anchor = (1,0,0.5,1))
    plt.setp(autotexts,size=8,weight="bold")
	#Titulo de la figura
    ax.set_title(title,fontsize=12,fontweight='bold')
    #Se almacena la figura
    savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1
    
    return num_imagen
	
'''
representacion_1_figura_lista_ordenada:
	Funcion que representa una lista ordenada en formato de barras y una linea de unión.
	Se debe indicar si la prueba es para IPv4 o IPv6 para cambiar el color de las barras.
	Se almacena la gráfica en un directorio.
	
'''
def representacion_1_figura_lista_ordenada(lista,tamano,bar_width,opacity,
                                        ylabel,xlabel,title,num_imagen,fecha,url,tipo_ip):
    # Color de las barras en funcion del tipo de ip
    if tipo_ip == "IPv4":
	
        color1 = "b"
		
    else:
	
        color1 = "y"
	
	# Se crea la figura y se anaden caracteristicas
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)
	
	# Se anaden los distintos elementos de la figura
    n_groups = len(lista)
	
    index = np.arange(n_groups)
	
    ax.plot(lista,color = "r")
    rects1 = ax.bar(index,lista,bar_width,alpha = opacity,color=color1)

	#Se anaden caracteristicas de los ejes y titulo
    ax.set_xticks([],[])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    
	#Se almacena la figura
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
    num_imagen = num_imagen + 1

    return num_imagen


'''-------    main     -------'''
#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8

#Variable utilizada para almacenar la imagen
num_imagen = 1

#Lista de todos los RRCs disponibles
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]

#Fecha de los datos
fecha = "20180110-20180110"

#URL con ubicación de los ficheros de datos (CSVs)
url_origen = "ResultadosCSV/Prefijos/DiaRCC/prefijos_"

#URL con ubicacion donde se almacenan las imagenes
url_imagen = "ResultadosCSV/Prefijos_imagenes/AS_origen_"

#Variable de control del tiempo
start_time = time()

#Bucle para unir toda la informacion de prefijos de los distintos colectores en un dataframe
contador = 0
for version_rrc in rrc:

    if contador == 0:
	
        data_origen = pd.read_csv(url_origen+fecha+version_rrc+".csv",sep=",")
        contador = 1
		
    else:
	
        data_origen = data_origen.append(pd.read_csv(url_origen+fecha+version_rrc+".csv",sep=","))

#Variables para controlar el numero de monitores IP que cumplen con el filtro
numero_monitores_ipv4 = 0
numero_monitores_ipv6 = 0
#Listas para anadir la cantidad de prefijos distintos
lista_ipv4 = []
lista_ipv6 = []

#Bucle que recorre todos los monitores y comprueba la cantidad de prefijos distintos,
# Además, se indica los monitores que superan el filtro para ser monitores proveedores.
for monitor in data_origen.Monitor.unique():

    mask_monitor = data_origen["Monitor"] == monitor
    data_monitor = data_origen[mask_monitor]
	
	# Se comprueba si el monitor es de tipo IPv4 o IPv6
    try:
        socket.inet_aton(monitor)
		
        if data_monitor.Prefijos.sum() > 0:
		
            lista_ipv4.append(data_monitor.Prefijos.sum())
			
			#Filtro de monitores para IPv4
            if data_monitor.Prefijos.sum() > 200000:
			
                numero_monitores_ipv4 = numero_monitores_ipv4 + 1
				
    except socket.error:
	
        if data_monitor.Prefijos.sum() > 0:

            lista_ipv6.append(data_monitor.Prefijos.sum())
			
			#Filtro de monitores para IPv6
            if data_monitor.Prefijos.sum() > 20000:
			
                numero_monitores_ipv6 = numero_monitores_ipv6 + 1
				
print(numero_monitores_ipv4)
print(numero_monitores_ipv6)

#Se ordena las listas para su representacion
lista_ipv4.sort()
lista_ipv6.sort()
lista_ipv6_final = []

#Se elimina un outlier presente
for x in lista_ipv6:
    if x < 200000:
        lista_ipv6_final.append(x)
		
#Se representa el numero de prefijos por monitor IPv4"
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ipv4,(10,5),bar_width,opacity,
                                        "Numero de prefijos","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")
										
#Se representa el numero de prefijos por monitor IPv6"
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ipv6_final,(10,5),bar_width,opacity,
                                        "Numero de prefijos","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Se representa la figura de distribucion por tipo de monitor (proveedor o peer/cliente)
lista_pie = [numero_monitores_ipv6,len(lista_ipv6)-numero_monitores_ipv6,
             numero_monitores_ipv4,len(lista_ipv4)-numero_monitores_ipv4]
labels_pie = ["Monitores IPv6 Proveedores", "Monitores IPv6 Peers/Clientes","Monitores IPv4 Proveedores", "Monitores IPv4 Peers/Clientes"]
title = ""
num_imagen = representacion_pie((10,6),lista_pie,labels_pie,"Leyenda de AS",title,num_imagen,fecha,url_imagen,"Monitores")

