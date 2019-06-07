#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel AS_PATH y 
realiza distintas funciones/agrupaciones para obtener distintas representaciones a este nivel

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

'''-------    FUNCIONES     -------'''

'''representacion_1_figura_diccionarios:
	Funcion que representa una figura a partir de un diccionario que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_diccionarios(diccionario,tamano,bar_width,opacity,
                                        rotation,ylabel,xlabel,title,num_imagen,fecha,url):
    
    #Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

    #Obtengo el numero de elementos del diccionario
    n_groups = len(diccionario)
    index = np.arange(n_groups)

    #Plot de tipo bar con los elementos del diccionario
    rects1 = ax.bar(index,list(diccionario.values()),bar_width,alpha = opacity,color = "c")
    
    #Anado informacion sobre la grafica y los ejes
    ax.set_xticks(index)
    ax.set_xticklabels(list(diccionario.keys()),rotation = rotation)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
    num_imagen = num_imagen + 1

    return num_imagen

'''informacion_distancia_prep_to_origen:
	Funcion que procesa la columna de "Lista de la distancia de ASes que realizan AS_PATH prepending al origen"
	Se obtiene todos los elementos de la columna y se modifica la lista para finalmente
	devolver un tipo contador con las distancias al origen existentes
'''
def informacion_distancia_prep_to_origen(data_prepending):

	#Obtencion de la columna del DataFrame de "DistanciaASesPrepending"
    lista_distancias_prep = data_prepending["DistanciaASesPrepending"].tolist()
    lista_distancias_prep2 = []
    
	#Debido a que la informacion de los elementos de la columna no es leida como lista, se modifica para
	# a partir de los elementos formar la lista de distancias
    for x in lista_distancias_prep:
    
        if type(x) == str:
        
            x= x.split("[")[1].split("]")[0]
            numero_elementos = len(x.split(", "))
            x = x.split(", ")
            
            for i in range(numero_elementos):
            
                lista_distancias_prep2.append(int(x[i]))

	# Se crea el Contador de los elementos de la lista
    contador_distancias_prep = collections.Counter(lista_distancias_prep2)

    return contador_distancias_prep

'''informacion_cantidad_prefijos_anunciados:
	Funcion que procesa la cantidad de prefijos anunciados agrupando en distintos grupos indicados
	a traves del parametro umbral.
	Finalmente se devuelve una lista con 6 categorias, separadas por los umbrales y con etiquetas
	para su identificacion
'''
def informacion_cantidad_prefijos_anunciados(data,umbral):

	#Obtencion de la columna "PrefijosAnunciados"
    lista_PrefijosAnunciados = data["PrefijosAnunciados"].tolist()
    cantidad_PrefijosAnunciados = [0]*(len(umbral)+1)
    
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
			
	#Anado el nombre de cada categoria
    labels = [str(umbral[0]-1) + " Prefijo",str(umbral[0]) + " a " + str(umbral[1]-1) + " Prefijos",
              str(umbral[1]) + " a " + str(umbral[2]-1) + " Prefijos",str(umbral[2]) + " a " + str(umbral[3]-1) + " Prefijos",
              str(umbral[3]) + " a " + str(umbral[4]-1) + " Prefijos","Mas de " + str(umbral[4]) + " Prefijos"]
			  
    return [cantidad_PrefijosAnunciados,labels]

'''func:
	Funcion auxiliar utilizada para establecer el formato de la representacion
	de tipo diagrama circular
'''
def func(pct,allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.2f}%\n({:d} aspaths) ".format(pct,absolute)

'''representacion_pie:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
	La figura es un diagrama de circular.
	Se establece parametros para caracterizar la figura, incluyendo la leyenda.
	La figura se almacena en la URL indicada
'''
def representacion_pie(tamano,lista,labels,title_leyenda,title,num_imagen,fecha,url_imagen):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(figsize = tamano,subplot_kw = dict(aspect="equal"))
	
	#Plot de tipo diagrama circular con los elementos de la lista
    wedges,texts,autotexts = ax.pie(lista,autopct=lambda pct: func(pct,lista),textprops=dict(color="w"))
	
	# Se anade caracteristicas de la leyenda, texto y titulo
    ax.legend(wedges,labels,title = title_leyenda,loc = "center left", bbox_to_anchor = (1,0,0.5,1))
    plt.setp(autotexts,size=8,weight="bold")
    ax.set_title(title,fontsize=12,fontweight='bold')
    
	#almaceno la figura en la url indicada
    savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
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

	#Unicamente IPv4
    data_ipv4 = data[mask_ipv4 & mask_ipv6_n]
	#Unicamente IPv6
    data_ipv6 = data[mask_ipv6 & mask_ipv4_n]
	#Ambos tipos de IP
    data_ip = data[mask_ipv4 & mask_ipv6]

	#Obtencion de la longitud total de cada tipo de IP (o ambos)
    aspath_ipv4 = len(data_ipv4)
    aspath_ipv6 = len(data_ipv6)
    aspath_ip = len(data_ip)

    return [aspath_ipv4,aspath_ipv6,aspath_ip,aspath_totales]

'''lista_porcentaje_distancia:
	Funcion que obtiene un diccionario con porcentajes de los distintos elementos 
	presentes en un contador.
'''
def lista_porcentaje_distancia(contador_distancias_prep,valor_maximo):

    longitud_dicc = len(contador_distancias_prep)
    dicc_porcentajes = {}
    
	#Para cada longitud se determina su porcentaje y se anade al diccionario
    for i in range(longitud_dicc):
        dicc_porcentajes.update({i:contador_distancias_prep.get(i)/valor_maximo})
		
    return dicc_porcentajes

'''representacion_1_figura_contadores:
	Funcion que representa una figura a partir de un elemento contador que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_contadores(contador,tamano,ylabel,xlabel,title,num_imagen,fecha,url,limit):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)
	
	#Plot de tipo bar con los elementos del contador
    ax.bar(contador.keys(),contador.values())
	
	#Anado informacion sobre la grafica y los ejes
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)    
    ax.grid()
    if limit != None:
        ax.set_xlim(limit)

	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen
	
'''representacion_1_figura_lista:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_lista(lista,labels_lista,tamano,ylabel,xlabel,title,num_imagen,fecha,url,bar_width,opacity,rotation):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

    n_groups = len(lista)
    index = np.arange(n_groups)
	
	#Plot de tipo bar con los elementos de la lista
    rects1 = ax.bar(index,lista,bar_width,alpha = opacity)

	#Anado informacion sobre la grafica y los ejes
    ax.set_xticks(index)
    ax.set_xticklabels(labels_lista,rotation=rotation)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    
	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
	
    num_imagen = num_imagen + 1

    return num_imagen

'''representacion_distOrigen_distintas_longaspath:
	Funcion que representa distintas figuras relacionadas con la distancia al AS_origen de
	los ASes que realizan AS_PATH prepending para distintas longitudes de AS_PATH que
	se anaden por argumento (longitudes)
	
'''
def representacion_distOrigen_distintas_longaspath(data_prepending,longitudes,num_imagen,fecha,url_imagen,bar_width,opacity):

	#Realizo la representación para cada longitud de AS_PATH de la lista de longitudes
    for z in longitudes:
        
		#Aplico la mascara de longitud de AS_PATH al dataframe
        mask_len_prep = data_prepending["LongitudASPATH"]==z
        data_prepending_len = data_prepending[mask_len_prep]

		#Obtengo la columna de distancias al AS origen de los ASes que realizan prepending
        lista_distancias_prep = data_prepending_len["DistanciaASesPrepending"].tolist()
        lista_distancias_prep2 = []
        
		#Formateo la columna para obtener la lista con el formato adecuado
        for x in lista_distancias_prep:
            
            if type(x) == str:
               
                x= x.split("[")[1].split("]")[0]
                numero_elementos = len(x.split(", "))
                x = x.split(", ")
                
                for i in range(numero_elementos):
               
                    lista_distancias_prep2.append(int(x[i]))
        
		#Convierto la lista en contador y obtengo el porcentaje de cada elemento individual
        contador_distancias_prep = collections.Counter(lista_distancias_prep2)
        dicc_porcentaje = lista_porcentaje_distancia(contador_distancias_prep,len(lista_distancias_prep2))
		
		#Representacion con ejes distancia al AS origen y Numero de AS_PATHs
        title = ""
        num_imagen = representacion_1_figura_contadores(contador_distancias_prep,(10,5),"Número aspaths",
                "Distancia al origen",title,num_imagen,fecha,url_imagen,None)
        
		#Representacion con ejes distancia al AS origen y porcentaje
        title = ""
        num_imagen = representacion_1_figura_diccionarios(dicc_porcentaje,(10,5),bar_width,opacity,
                            "vertical","Porcentaje","Distancia al origen",title,num_imagen,fecha,url_imagen)

    return num_imagen


'''-------    main     -------'''

#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8

#Variable utilizada para almacenar la imagen en distintas ubicaciones
num_imagen = 1

#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]

#URLs donde se encuentran los ficheros CSV
url = "ResultadosCSV/ASPATH/DiaRCC/ASPATH_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/ASPATH_imagenes/DiaRCC/ASPATH_"

#Se agrupa todos los datos de los distintos CSV en un unico dataframe
contador = 0
for version_rrc in rrc:

    if contador == 0:
	
        data = pd.read_csv(url+fecha+version_rrc+".csv",sep=",")
        contador = 1
		
    else:
	
        data = data.append(pd.read_csv(url+fecha+version_rrc+".csv",sep=","),ignore_index = True,sort = True)

#Obtengo informacion de la distribucion IP de los AS_PATHs
[aspath_ipv4,aspath_ipv6,aspath_ip,aspath_totales] = informacion_ip(data)

#Lista y etiquetas de la distribucion IP de los AS_PATHs
lista_ip = [aspath_ipv4, aspath_ipv6,aspath_ip]
labels_ip = ["Entradas IPv4", "Entradas IPv6","Entradas IPv4 y IPv6"]
title = ""

#Representacion distribucion IP de los AS_PATHs en un diagrama circular
num_imagen = representacion_pie((10,6),lista_ip,labels_ip,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen)

#Obtencion de la cantidad de monitores distintos por los que pasa un AS_PATH (tipicamente 1 o 2)
cantidad_monitores = collections.Counter(data["Monitor"].tolist())

#Representacion de la cantidad de monitores distintos por los que pasa un AS_PATH en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(cantidad_monitores,(10,5),"Número aspaths",
                "Número monitores",title,num_imagen,fecha,url_imagen,None)

#Distribucion de la informacion de cantidad de prefijos anunciados por AS_PATH, con umbrales de (2,5,20,
#100,1000) prefijos distintos
[cantidad_PrefijosAnunciados,lista_labels_PrefijosAnunciados] = informacion_cantidad_prefijos_anunciados(data
    ,[2,5,20,100,1000])

#Representacion de la informacion de cantidad de prefijos distintos anunciados por AS_PATH en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_lista(cantidad_PrefijosAnunciados,lista_labels_PrefijosAnunciados,(10,5),
                    "Número aspaths","Número prefijos distintos",title,num_imagen,fecha,url_imagen,bar_width,opacity,"vertical")

#Obtencion de la cantidad de veces que se realiza AS_PATH prepending y que no se realiza por AS_PATH
num_aspath_prepending = data["Prepending"].sum()
num_aspath_no_prepending =  aspath_totales-num_aspath_prepending

#Creacion lista y etiquetas de AS_PATHs sobre los que se observa AS_PATH prepending y sobre los que no se observa
lista_prep = [num_aspath_prepending, num_aspath_no_prepending]
labels_prep = ["aspaths con prepending", "aspaths sin prepending"]
title = ""

#Representacion de distribucion de AS_PATHs con AS_PATH prepending y sin AS_PATH prepending, en un diagrama de barras
num_imagen = representacion_pie((10,6),lista_prep,labels_prep,"Leyenda de aspaths",title,num_imagen,fecha,url_imagen)

#Obtengo informacion sobre el numero de ASes que hacen AS_PATH prepending, cuando lo hay
mask_prepending = data["Prepending"] > 0
data_prepending = data[mask_prepending]
numASes_prepending = collections.Counter(data_prepending["Num_ASesPrepending"].tolist())

#Representacion del numero de ASes que hacen AS_PATH prepending por AS_PATH en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(numASes_prepending,(10,5),"Número aspaths",
                "Número ASes",title,num_imagen,fecha,url_imagen,None)

#Obtengo informacion de la secuencia mas larga de repeticion de AS_PATH prepending cuando lo hay
secuencia_maslarga = collections.Counter(data_prepending["MayorPrepending"].tolist())

#Representacion de la secuencia mas larga de repeticion de AS_PATH prepending (cuando lo hay) por AS_PATH
#en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(secuencia_maslarga,(10,5),"Número aspaths",
                "Prepending mas largo por aspath",title,num_imagen,fecha,url_imagen,(1,30))

#Obtengo contador con informacion de la longitud de ASPATH
contador_long_aspath = collections.Counter(data["LongitudASPATH"].tolist())

#Representacion de informacion de longitud de AS_PATH en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(contador_long_aspath,(10,5),"Número aspaths",
                "Longitud aspaths",title,num_imagen,fecha,url_imagen,(0,25))

#Obtengo contador con informacion de la longitud de ASPATH cuando se observa AS_PATH prepending
contador_long_aspath = collections.Counter(data_prepending["LongitudASPATH"].tolist())

#Representacion de informacion de longitud de AS_PATH cuando se observa AS_PATH prepending en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(contador_long_aspath,(10,5),"Número aspaths",
                "Longitud aspaths",title,num_imagen,fecha,url_imagen,(0,25))

#Obtengo un contador con informacion de la distnacia al origen de los ASes que realizan AS_PATH prepending
contador_distancias_prep = informacion_distancia_prep_to_origen(data_prepending)

#Representacion de la distancia al origen de los ASes que realizan AS_PATH prepending en un diagrama de barras
title = ""
num_imagen = representacion_1_figura_contadores(contador_distancias_prep,(10,5),"Número aspaths",
                "Distancia al origen",title,num_imagen,fecha,url_imagen,None)

#Representacion dependiente de distancia al origen de los ASes que realizan AS_PATH prepending en funcion
# de la distancia de AS_PATH (por defecto una lista de rango (3 a 10)
num_imagen = representacion_distOrigen_distintas_longaspath(data_prepending,list(range(3,10)),num_imagen,fecha,url_imagen,bar_width,opacity)


