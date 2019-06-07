#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel de longitudes de prefijo y 
realiza distintas funciones/agrupaciones para obtener distintas representaciones a este nivel

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/Longitudes_imagenes/DiaRCC/", ya que es donde se almacenan las imagenes.

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

'''-------    FUNCIONES     -------'''


'''func:
	Funcion auxiliar utilizada para parametros de la funcion representacion pie
'''
def func(pct,allvals,nombre):

    absolute = int(pct/100.*np.sum(allvals))
    prueba = "{:.2f}%\n({:d} " + nombre+ " ) "
	
    return prueba.format(pct,absolute)

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
	
'''informacion_numero_longitudes_monitor:
	Funcion que a partir de un dataframe con informacion de longitudes de prefijo por monitor obtiene el
	numero de longitudes distintos por monitor (dependiendo de si es de tipo IPv4 o IPv6) y lo devuelve en
	una lista.
'''

def informacion_numero_longitudes_monitor(data_long_monitores):
    

    lista_longitudes_monitores = [[],[]]

    #Recorro el dataframe por todos los monitores disponibles.
    for monitor in data_long_monitores.Monitor.unique():
		
		#Aplico mascara del monitor y obtengo su dataframe
        mask_monitor = data_long_monitores["Monitor"] == monitor
        data_monitores = data_long_monitores[mask_monitor]
		
		#Obtengo la cantidad de longitudes de prefijo distintos por monitor
        longitudes_monitor = len(data_monitores.Longitud.unique())
		
		#Almaceno en lista segun monitor IPv4 o IPv6
        try:
		
            socket.inet_aton(monitor)
            lista_longitudes_monitores[0].append(longitudes_monitor)
            
       
        except socket.error:
        
            lista_longitudes_monitores[1].append(longitudes_monitor)

    return lista_longitudes_monitores


'''representacion_1_figura_contadores:
	Funcion que representa una figura a partir de un elemento contador que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_contadores(contador,tamano,ylabel,xlabel,title,num_imagen,fecha,url,tipo_ip):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

	#Plot de tipo bar con los elementos del contador
    ax.bar(contador.keys(),contador.values())

	#Anado informacion sobre la grafica y los ejes
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)    
    ax.grid()
    if tipo_ip == "IPv4":
        ax.set_xlim([0,32])

	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''representacion_informacion_global_ip:
	Funcion que representa una figura de 3 graficas distintas, a partir de un dataframe que se pasa como parametro.
	Las graficas son muestran distintos resultados en funcion de la longitud de prefijo.
	Las figuras son:
		1. Numero de entradas BGP totales y Numero de entradas BGP sobre los que se ha observado AS_PATH prepending
		2. Porcentaje de realizacion de AS_PATH prepending para cada longitud.
		3. Porcentaje de realización de AS_PATH prepending para longitudes que tengan un minimo numero de entradas BGP
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en una URL
'''
def representacion_informacion_global_ip(data_ip,tamano,ylabel1,ylabel2,ylabel3,title1,title2,title3,num_imagen,url,fecha):
    
	#Se ordena el dataframe por longitud de prefijo en orden ascendente.
    data_ip = data_ip.sort_values(by='Longitud',ascending=True)
	#Se obtiene el porcentaje para cada longitud de realizacion de AS_PATH prepending
    data_ip.eval("Porcentaje = Prepending / Total",inplace=True)

	#Se crea la figura de 3 elementos
    fig,ax = plt.subplots(nrows = 3, ncols = 1,figsize=tamano)

	#Se anaden los plots de cada imagen
    data_ip.plot(x = 'Longitud',y = "Total",ax = ax[0],kind='bar',color = "b")
    data_ip.plot(x = 'Longitud',y = "Prepending",ax = ax[0],kind='bar',color = "g")
    data_ip.plot(x = 'Longitud',y = "Porcentaje",ax = ax[1],kind='bar',color = "b")
    
	#Se aplica un filtro para unicamente elegir longitudes de prefijo que lo superen
    mask_porcentaje = data_ip["Total"] >= (data_ip["Total"].max()/100*2)
    data_ip = data_ip[mask_porcentaje]
    data_ip.plot(x = 'Longitud',y = "Porcentaje",ax = ax[2],kind='bar',color = "c")
    
	#Se anaden caracteristicas de los ejes de cada figura
    ax[0].set_ylabel(ylabel1)
    ax[0].set_title(title1)
    
    ax[1].set_ylabel(ylabel2)
    ax[2].set_ylabel(ylabel3)
    
    ax[1].set_title(title2)
    ax[2].set_title(title3)
    ax[0].grid()
    ax[1].grid()
    ax[2].grid()
	
	#Se almacena la figura
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
    num_imagen = num_imagen + 1  
       
    return num_imagen

'''informacion_longitudes_27_28:
	Funcion que realiza dos actividades distintas:
	Primero, para cada longitud de AS_PATH obtiene el numero de entradas BGP con longitud de prefijo 27 y 28 
		Esto se realiza de manera especifica para comprobar un rasgo de estas longitudes. (OPCIONAL)
	Segundo: Se muestra la informacion de porcentaje de realizacion de prepending a medida que se varia
		la longitud de AS_PATH para comprobar su influencia en los resultados.
'''
def informacion_longitudes_27_28(data_ipv4_long,num_imagen,url,fecha):

    dicc_long27 = {}
    dicc_long28 = {}
	#Ordenacion del dataframe por longitud de AS_PATH
    data_ipv4_long=data_ipv4_long.sort_values(by="LongitudASPATH",ascending=True)
	
	#Recorro el DataFrame por cada longitud de AS_PATH disponible
    for long_aspath in data_ipv4_long["LongitudASPATH"].unique():
        
		#creo y aplico mascara de la longitud de AS_PATH
        mask_aspath = data_ipv4_long["LongitudASPATH"] == long_aspath
        data_longitud = data_ipv4_long[mask_aspath] 
        
		#creo y aplico mascara de la longitud de prefijo 27 y 28
        mask_27 = data_longitud["Longitud"] == 27 
        mask_28 = data_longitud["Longitud"] == 28 
        data_longitud_27 = data_longitud[mask_27]
        data_longitud_28 = data_longitud[mask_28]
		
		#Se obtiene el numero total de entradas BGP para las longitudes y por cada longitud de AS_PATH
        if len(data_longitud_27) != 0:
		
            dicc_long27.update({long_aspath:data_longitud_27["Total"].values[0]})
			
        else:
		
            dicc_long27.update({long_aspath:0})

        if len(data_longitud_28) != 0:
		
            dicc_long28.update({long_aspath:data_longitud_28["Total"].values[0]})
			
        else:
		
            dicc_long28.update({long_aspath:0})
        
        #Del DataFrame de longitud de AS_PATH se seleccionan valores que superen un determinado filtro
        mask_total_anuncios = data_longitud["Total"] > data_longitud["Total"].max()/100
        data_longitud = data_longitud[mask_total_anuncios] 
		
		#Solo se representa informacion para longitudes de AS_PATH entre 2 a 9
        if long_aspath > 1 and long_aspath < 10:
			
			#Se ordena por longitud de prefijo para la representacion
            data_longitud = data_longitud.sort_values(by='Longitud',ascending=True)
			
			#Se obtiene el porcentaje de realizacion de AS_PATH prepending para cada longitud independientemente
            data_longitud.eval("Porcentaje = Prepending / Total",inplace=True)
			
			#Se crea la figura y se representa
            fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=(10,5))

            data_longitud.plot(x = 'Longitud',y = "Porcentaje",ax = ax,kind='bar',color = "b")
            ax.set_ylabel("Porcentaje")
            ax.grid()
            ax.set_title("")
			
			#Se almacena la figura
            savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
            num_imagen = num_imagen + 1  
        
    return [dicc_long27,dicc_long28,num_imagen]

	
'''representacion_dicc_longitud:
	Funcion que representa dos diccionarios en una figura e imagen de tipo diagrama de barras.
'''
def representacion_dicc_longitud(dicc1,dicc2,tamano,bar_width,opacity,label1,label2,rotation,ylabel,title,xlabel,url,fecha,num_imagen):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

	#Obtengo el numero de elementos del diccionario (ambos diccionarios coinciden en numero de elementos)

    n_groups = len(dicc1)
    index = np.arange(n_groups)

	#Plot de tipo bar con los elementos del diccionario

    rects1 = ax.bar(index,list(dicc1.values()),bar_width,alpha = opacity,
                    color='c',label = label1)
    rects2 = ax.bar(index+bar_width,list(dicc2.values()),bar_width,alpha = opacity,
                    color='r',label = label2)
					
    #Anado informacion sobre la grafica y los ejes
    ax.set_xticks(index)
    ax.set_xticklabels(list(dicc1.keys()),rotation = rotation)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
	
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
    num_imagen = num_imagen + 1  
    
    return num_imagen


'''-------    main     -------'''

#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8

#Variable utilizada para almacenar la imagen
num_imagen = 1

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]
	   
#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url_long_monitor = "ResultadosCSV/Longitudes/DiaRCC/Longitudes_monitores_"
url_long_total_ipv4 = "ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv4_"
url_long_total_ipv6 = "ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv6_"
url_long_aspath_ipv4 = "ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv4_longaspath_"
url_long_aspath_ipv6 = "ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv6_longaspath_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/Longitudes_imagenes/DiaRCC/Longitudes_monitores_"

#Se agrupa todos los datos de los distintos CSV en un dataframe unico para cada tipo de datos (se unen la info de colectores para cada tipo de datos)
contador = 0
for version_rrc in rrc:
    if contador == 0:
        data_long_monitores = pd.read_csv(url_long_monitor+fecha+version_rrc+".csv",sep=",")
        data_ipv4 = pd.read_csv(url_long_total_ipv4+fecha+version_rrc+".csv",sep=",")
        data_ipv6 = pd.read_csv(url_long_total_ipv6+fecha+version_rrc+".csv",sep=",")
        data_ipv4_long = pd.read_csv(url_long_aspath_ipv4+fecha+version_rrc+".csv",sep=",")
        data_ipv6_long = pd.read_csv(url_long_aspath_ipv6+fecha+version_rrc+".csv",sep=",")

        contador = 1
    else:
        data_long_monitores = data_long_monitores.append(pd.read_csv(url_long_monitor+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)
        data_ipv4 = data_ipv4.append(pd.read_csv(url_long_total_ipv4+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)
        data_ipv6 = data_ipv6.append(pd.read_csv(url_long_total_ipv6+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)
        data_ipv4_long = data_ipv4_long.append(pd.read_csv(url_long_aspath_ipv4+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)
        data_ipv6_long = data_ipv6_long.append(pd.read_csv(url_long_aspath_ipv6+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)

# Se aplican mascaras para agrupar por longitud de prefijo o por combinacion de longitud de prefijo y longitud de AS_PATH
data_ipv4 = data_ipv4.groupby(["Longitud"],as_index = False).sum()
data_ipv6 = data_ipv6.groupby(["Longitud"],as_index = False).sum()
data_ipv4_long = data_ipv4_long.groupby(["Longitud","LongitudASPATH"],as_index = False).sum()
data_ipv6_long = data_ipv6_long.groupby(["Longitud","LongitudASPATH"],as_index = False).sum()

#Obtencion del numero de longitudes de prefijos distintos por monitor 
lista_longitudes_monitores = informacion_numero_longitudes_monitor(data_long_monitores)

contador_longitudes_monitores_ipv4_totales = collections.Counter(lista_longitudes_monitores[0])
contador_longitudes_monitores_ipv6_totales = collections.Counter(lista_longitudes_monitores[1])

#Representacion del numero de longitudes de prefijo distintos por monitor IPv4 e IPv6
title = ""
num_imagen = representacion_1_figura_contadores(contador_longitudes_monitores_ipv4_totales,(10,5),"Numero de Monitores",
                                                "Numero de Longitudes",title,num_imagen,fecha,url_imagen,"IPv4")
title = ""
num_imagen = representacion_1_figura_contadores(contador_longitudes_monitores_ipv6_totales,(10,5),"Numero de Monitores",
                                                "Numero de Longitudes",title,num_imagen,fecha,url_imagen,"IPv6")


#Representacion de informacion global de cada longitud de prefijo independientemente del resto para IPv4 e IPv6
title1 = ""
title2 = ""
title3 = ""
num_imagen = representacion_informacion_global_ip(data_ipv4,(15,20),"Numero de entradas","Porcentaje","Porcentaje",
                    title1,title2,title3,num_imagen,url_imagen,fecha)

title1 = ""
title2 = ""
title3 = ""
num_imagen = representacion_informacion_global_ip(data_ipv6,(15,20),"Numero de entradas","Porcentaje","Porcentaje",
                    title1,title2,title3,num_imagen,url_imagen,fecha)

#Representacion de influencia de la longitud de AS_PATH en los resultados y obtencion de la cantidad de entradas BGP 
# con longitudes de prefijo 27 y 28 para cada longitud de prefijo
[dicc_long27,dicc_long28,num_imagen] = informacion_longitudes_27_28(data_ipv4_long,num_imagen,url_imagen,fecha)

#Representacion de la cantidad de entradas BGP para longitudes de prefijo 27 y 28 en funcion de la longitud de AS_PATH
title = ""
num_imagen = representacion_dicc_longitud(dicc_long27,dicc_long28,(10,5),bar_width,opacity,"Longitud de prefijo 27",
                    "Longitud de prefijo 28","vertical","Numero de entradas",title,"Longitud aspath",url_imagen,fecha,num_imagen)


