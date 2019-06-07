#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel ASes Transito  y 
realiza distintas funciones/agrupaciones para obtener distintas representaciones a este nivel

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/ASes_imagenes/DiaRCC/", ya que es donde se almacenan las imagenes.



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
    savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
    num_imagen = num_imagen + 1
    
    return num_imagen


'''informacion_general_monitores:
	Funcion que obtiene informacion de ASes por monitor de manera independiente.
	Se obtiene la cantidad de ASes vistos por cada monitor, la cantidad y porcentaje de ASes que realizan AS_PATH prepending
	por cada monitor.
	Adicionalmente, se obtiene informacion del porcentaje de ASes que siempre realizan AS_PATH prepending en ese monitor 
	y la cantidad de ASes que nunca realizan prepending en ese monitor
'''
def informacion_general_monitores(lista_monitores_transito,data_transito):
    
	#Creacion de diccionarios y listas sobre las que se almacena distinta informacion
	
	#Informacion de la cantidad de ASes por monitor
    diccionario_monitores_ASes_validos = {}
    diccionario_monitores_ASes_validos_ipv6 = {}
    
	#Informacion de la cantidad/porcentaje de ASes que han realizado AS_PATH prepending por monitor
    lista_monitores_ASes_validos_prep_ipv4 = []
    lista_monitores_ASes_validos_prep_ipv6 = []
    lista_monitores_ASes_validos_porc_prep_ipv4 = []
    lista_monitores_ASes_validos_porc_prep_ipv6 = []
    
	#Informacion de porcentaje de ASes que realizan AS_PATH prepending siempre por monitor
    lista_monitores_ASes_porc_validos_prep_siempre_ipv4 = []
    lista_monitores_ASes_porc_validos_prep_siempre_ipv6 = []
    
	#Informacion de porcentaje de ASes que nunca realizan AS_PATH prepending por monitor
    lista_monitores_ASes_porc_validos_prep_nunca_ipv4 = []
    lista_monitores_ASes_porc_validos_prep_nunca_ipv6 = []

    #Recorrer el dataframe a traves de los distintos monitores
    for monitor_transito in lista_monitores_transito:
        
        #Creacion y utilización de mascaras para el monitor y para la realización de AS_PATH prepending
        mask_monitor = data_transito["Monitor"] == monitor_transito
        df_monitor = data_transito[mask_monitor]
        mask_prepending = df_monitor["Prepending"] > 0
        df_monitor_prep = df_monitor[mask_prepending]
		
        #Comprobacion si es un monitor de tipo IPv4 o IPv6
        try:
            
            socket.inet_aton(monitor_transito)

            #Obtencion de si el AS realiza prepending siempre o a veces en ese monitor
            C = np.where((df_monitor_prep["Prepending"] ==
                                         df_monitor_prep["Totales"]),1,0)
            total_prepending_siempre = C.sum()
            total_prepending_aveces = len(C) - total_prepending_siempre
            
			#Almacenamiento de estadisticas de monitor
            diccionario_monitores_ASes_validos.update({monitor_transito: len(df_monitor)})
            lista_monitores_ASes_porc_validos_prep_siempre_ipv4.append(total_prepending_siempre/len(df_monitor))
            lista_monitores_ASes_validos_prep_ipv4.append(len(df_monitor_prep))
            lista_monitores_ASes_validos_porc_prep_ipv4.append(len(df_monitor_prep)/len(df_monitor))
            lista_monitores_ASes_porc_validos_prep_nunca_ipv4.append((len(df_monitor)-len(df_monitor_prep))/len(df_monitor))     
            
        except socket.error:
        
            #Obtencion de si el AS realiza prepending siempre o a veces en ese monitor
            C = np.where((df_monitor_prep["Prepending"] ==
                                         df_monitor_prep["Totales"]),1,0)
            total_prepending_siempre = C.sum()
            total_prepending_aveces = len(C) - total_prepending_siempre
                
			#Almacenamiento de estadisticas de monitor
            diccionario_monitores_ASes_validos_ipv6.update({monitor_transito: len(df_monitor)})
            lista_monitores_ASes_porc_validos_prep_siempre_ipv6.append(total_prepending_siempre/len(df_monitor))
            lista_monitores_ASes_validos_prep_ipv6.append(len(df_monitor_prep))
            lista_monitores_ASes_validos_porc_prep_ipv6.append(len(df_monitor_prep)/len(df_monitor))
            lista_monitores_ASes_porc_validos_prep_nunca_ipv6.append((len(df_monitor)-len(df_monitor_prep))/len(df_monitor))     

            
    #Se ordenan las listas para facilitar la representacion posterior
    lista_monitores_ASes_validos_prep_ipv4.sort()
    lista_monitores_ASes_validos_prep_ipv6.sort()
    lista_monitores_ASes_validos_porc_prep_ipv4.sort()
    lista_monitores_ASes_validos_porc_prep_ipv6.sort()
    lista_monitores_ASes_porc_validos_prep_siempre_ipv4.sort()
    lista_monitores_ASes_porc_validos_prep_siempre_ipv6.sort()
    lista_monitores_ASes_porc_validos_prep_nunca_ipv4.sort()
    lista_monitores_ASes_porc_validos_prep_nunca_ipv6.sort()
    
    return [diccionario_monitores_ASes_validos,
            diccionario_monitores_ASes_validos_ipv6,lista_monitores_ASes_validos_prep_ipv4,
            lista_monitores_ASes_validos_prep_ipv6,lista_monitores_ASes_validos_porc_prep_ipv4,lista_monitores_ASes_validos_porc_prep_ipv6,
            lista_monitores_ASes_porc_validos_prep_siempre_ipv4,lista_monitores_ASes_porc_validos_prep_siempre_ipv6,
            lista_monitores_ASes_porc_validos_prep_nunca_ipv4,lista_monitores_ASes_porc_validos_prep_nunca_ipv6]


'''representacion_1_figura_diccionarios:
	Funcion que representa una figura a partir de un diccionario que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_diccionarios(diccionario,tamano,bar_width,opacity,
                                        label,rotation,ylabel,xlabel,title,num_imagen,fecha,url,tipo_ip):
    
	#Dependiendo del tipo de IP se elige el color de la gráfica
    if tipo_ip == "IPv4":
	
        color1 = "b"
		
    else:
	
        color1 = "y"
    
    #Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

    #Obtengo el numero de elementos del diccionario
    n_groups = len(diccionario)
    index = np.arange(n_groups)

    #Plot de tipo bar con los elementos del diccionario
    rects1 = ax.bar(index,list(diccionario.values()),bar_width,alpha = opacity,
                 color=color1,label=label)
    
    #Anado informacion sobre la grafica
    ax.set_xticks(index)
    ax.set_xticklabels(list(diccionario.keys()),rotation = rotation)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid()
    ax.legend()
    
	#Almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
    num_imagen = num_imagen + 1

    return num_imagen

'''representacion_1_figura_lista_ordenada:
	Funcion que representa una figura a partir de una lista que se pasa por parametro.
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

'''representacion_1_figura_contadores:
	Funcion que representa una figura a partir de un elemento contador que se pasa por parametro.
	La figura es un diagrama de barras.
	Se establece parametros para caracterizar los distintos ejes y se almacena la figura en 
	una URL
'''
def representacion_1_figura_contadores(contador,tamano,ylabel,xlabel,title,num_imagen,fecha,url):
    
	#Creo la figura de 1 fila y 1 columna del tamano indicado
    fig,ax = plt.subplots(nrows = 1, ncols = 1,figsize=tamano)

	#Plot de tipo bar con los elementos del contador
    ax.bar(contador.keys(),contador.values())
	
	#Anado informacion sobre la grafica y los ejes
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)    
    ax.grid()

	#almaceno la figura en la url indicada
    savefig(url+fecha+"_" + str(num_imagen),bbox_inches = "tight")
    num_imagen = num_imagen + 1

    return num_imagen

'''informacion_AStransito_prepending_cuantos_monitores:
	Funcion que devuelve informacion relacionada con los ASes:
		- Numero ASes totales agrupando colectores
		- Numero de ASes distintos que no realizan AS_PATH prepending en ningun monitor
		- Numero de ASes distintos que realizan AS_PATH prepending en algunas apariciones de algunos monitores.
		- Numero de ASes distintos que realizan AS_PATH prepending en algunas apariciones de todos los monitor
		Mismas ultimas 3 pruebas pero con ASes que aparecen en mas de 300 monitores distintos.

'''
def informacion_AStransito_prepending_cuantos_monitores(data_transito):
    
    diccionario_AStransito_info = {}
    
	#Recorro todos los distintos monitores del dataframe
    for monitor in data_transito.Monitor.unique():
        
		#Creo y aplico mascara de monitor y de AS_PATH prepending
        mask_monitor = data_transito["Monitor"] == monitor
        data_monitor = data_transito[mask_monitor]
        mask_monitor_prep = data_monitor["Prepending"] > 0
        data_monitor_prep = data_monitor[mask_monitor_prep]
		
		#Obtengo lista con todos los ASes distintos vistos y todos los ASes distintos que han realizado AS_PATH prepending al menos una vez
        lista_AS_monitor = data_monitor.ASTransito.unique().tolist()
        lista_AS_monitor_prep = data_monitor_prep.ASTransito.unique().tolist()
		
		#Almaceno en un diccionario la informacion de monitor y lista de ASes totales + lista de ASes que han realizado prepending al menos una vez
        diccionario_AStransito_info.update({monitor:[lista_AS_monitor,lista_AS_monitor_prep]})

    diccionario_AStransito_infototal = {}
	
	#Recorro el anterior diccionario
    for i,v in enumerate(diccionario_AStransito_info.items()):
        
		#Recorro cada AS del monitor
        for AS in v[1][0]:
        
            prepending = 0
			
			#Compruebo si ese AS ha realizado AS_PATH prepending al menos una vez
            if AS in v[1][1]:
            
                prepending = 1
            
			#Actualizacion diccionario con clave AS y values (Veces que se realiza AS_PATH prepending en distintos monitores + 
			# Monitores totales en los que aparece el AS (el segundo y tercer elemento del diccionario es el mismo))
            if not AS in diccionario_AStransito_infototal:            
            
                diccionario_AStransito_infototal.update({AS:[prepending,1,1]})
            
            else:
            
                lista_auxiliar = diccionario_AStransito_infototal.get(AS)
                diccionario_AStransito_infototal.update({AS:[lista_auxiliar[0]+prepending,
                                                      lista_auxiliar[1]+1,lista_auxiliar[2]+1]})
	
	#Obtengo el numero de ASes distintos contando la informacion de todos los colectores
    num_ASes =  len(diccionario_AStransito_infototal)
	
    num_no_prepending = 0
    num_algunos_prepending = 0
    num_todos_prep = 0
    
    num_no_prepending_filt = 0
    num_algunos_prepending_filt = 0
    num_todos_prep_filt = 0
    
    #Recorro los elementos del diccionario anterior
    for i,v in enumerate(diccionario_AStransito_infototal.items()):
        
		#Compruebo si se ha visto o no AS_PATH prepending
        if v[1][0] == 0:
        
            num_no_prepending = num_no_prepending + 1
        
        else:
			
			#Compruebo si se ha realizado AS_PATH prepending (al menos una vez) en todos los monitores o en algunos
            if v[1][0] != v[1][1]:
            
                num_algunos_prepending = num_algunos_prepending + 1
            
            else:
            
                num_todos_prep = num_todos_prep + 1
        
		#Si el AS aparece en mas de 300 monitores
        if v[1][2] > 300:
            
			#Compruebo si el AS ha realizado AS_PATH prepending en algun monitor
            if v[1][0] == 0:
        
                num_no_prepending_filt = num_no_prepending_filt + 1
        
            else:
			
				#Compruebo si se ha realizado AS_PATH prepending (al menos una vez) en todos los monitores o en algunos
                if v[1][0] != v[1][1]:
            
                    num_algunos_prepending_filt = num_algunos_prepending_filt + 1
            
                else:
            
                    num_todos_prep_filt = num_todos_prep_filt + 1
					
    return [num_ASes,num_no_prepending,num_algunos_prepending,num_todos_prep,
            num_no_prepending_filt,num_algunos_prepending_filt,num_todos_prep_filt]
    

'''informacion_AStransito_prepending_siempre_cuantos_monitores:
	Funcion que devuelve informacion relacionada con los ASes.
	La principal diferencia con la anterior funcion es que anteriormente se comprueba si el AS realiza AS_PATH prepending alguna vez por monitor
	Mientras que en esta ocasion debe realizarlo en todas las apariciones del AS por monitor
		- Numero ASes totales agrupando colectores
		- Numero de ASes distintos que no realizan AS_PATH prepending en todas sus apariciones en ningun monitor
		- Numero de ASes distintos que realizan AS_PATH prepending en todas sus apariciones de algunos monitores.
		- Numero de ASes distintos que realizan AS_PATH prepending en todas las apariciones de todos los monitores en los que esta presente.
		Mismas ultimas 3 pruebas pero con ASes que aparecen en mas de 300 monitores distintos.

'''
def informacion_AStransito_prepending_siempre_cuantos_monitores(data_transito):
    
    diccionario_AStransito_info = {}
	
	#Recorro todos los distintos monitores del dataframe
    for monitor in data_transito.Monitor.unique():
        
		#Creo y aplico mascara de monitor y de AS_PATH prepending
        mask_monitor = data_transito["Monitor"] == monitor
        data_monitor = data_transito[mask_monitor]
        mask_monitor_prep = data_monitor["Prepending"] > 0
        data_monitor_prep = data_monitor[mask_monitor_prep]
		
		#Obtengo lista con todos los ASes distintos vistos y todos los ASes distintos que han realizado AS_PATH prepending en todas sus apariciones para ese monitor
        C = np.where((data_monitor_prep["Prepending"] == data_monitor_prep["Totales"]),data_monitor_prep["ASTransito"],"0")
        lista_aux = C.tolist()
        lista_AS_monitor = data_monitor.ASTransito.unique().tolist()
        lista_AS_monitor_prep = elimina_ceros(lista_aux)
		
		#Almaceno en un diccionario la informacion de monitor y lista de ASes totales + lista de ASes que han realizado prepending siempre para ese monitor
        diccionario_AStransito_info.update({monitor:[lista_AS_monitor,lista_AS_monitor_prep]})

    diccionario_AStransito_infototal = {}
	
	#Recorro el anterior diccionario
    for i,v in enumerate(diccionario_AStransito_info.items()):
        
		#Recorro cada AS del monitor
        for AS in v[1][0]:
        
            prepending = 0
            
			#Compruebo si ese AS ha realizado AS_PATH prepending siempre en el monitor
            if AS in v[1][1]:
            
                prepending = 1
            
			#Actualizacion diccionario con clave AS y values (Veces que se realiza AS_PATH prepending en distintos monitores + 
			# Monitores totales en los que aparece el AS (el segundo y tercer elemento del diccionario es el mismo))
            if not AS in diccionario_AStransito_infototal:            
            
                diccionario_AStransito_infototal.update({AS:[prepending,1,1]})
            
            else:
            
                lista_auxiliar = diccionario_AStransito_infototal.get(AS)
                diccionario_AStransito_infototal.update({AS:[lista_auxiliar[0]+prepending,
                                                      lista_auxiliar[1]+1,lista_auxiliar[2]+1]})
	
	#Obtengo el numero de ASes distintos contando la informacion de todos los colectores	
    num_ASes =  len(diccionario_AStransito_infototal)
    num_no_prepending = 0
    num_algunos_prepending = 0
    num_todos_prep = 0
    
    num_no_prepending_filt = 0
    num_algunos_prepending_filt = 0
    num_todos_prep_filt = 0
    
     #Recorro los elementos del diccionario anterior
    for i,v in enumerate(diccionario_AStransito_infototal.items()):
        
		#Compruebo si se ha visto o no AS_PATH prepending
        if v[1][0] == 0:
        
            num_no_prepending = num_no_prepending + 1
        
        else:
			#Compruebo si se ha realizado AS_PATH prepending (en todas sus apariciones por monitor) en todos los monitores o en algunos
            if v[1][0] != v[1][1]:
            
                num_algunos_prepending = num_algunos_prepending + 1
            
            else:
            
                num_todos_prep = num_todos_prep + 1
        
		#Si el AS aparece en mas de 300 monitores
        if v[1][2] > 300:
            
			#Compruebo si el AS ha realizado AS_PATH prepending (en todas sus apariciones en algun monitor) o no
            if v[1][0] == 0:
        
                num_no_prepending_filt = num_no_prepending_filt + 1
        
            else:
				
				#Compruebo si se ha realizado AS_PATH prepending (en todas sus apariciones en todos los monitores o en algunos)
                if v[1][0] != v[1][1]:
            
                    num_algunos_prepending_filt = num_algunos_prepending_filt + 1
            
                else:
            
                    num_todos_prep_filt = num_todos_prep_filt + 1
					
    return [num_ASes,num_no_prepending,num_algunos_prepending,num_todos_prep,
            num_no_prepending_filt,num_algunos_prepending_filt,num_todos_prep_filt]

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
'''elimina_ceros:
	Funcion que devuelve una lista identica a la pasada por parametro, pero eliminando los elementos con valor igual a cero
'''
def elimina_ceros(original):

    nueva=[]
	
    for dato in original:
	
        if dato != "0":
		
            nueva.append(dato)
			
    return nueva

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

#Variable utilizada para almacenar la imagen
num_imagen = 1

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]
#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url_transito = "ResultadosCSV/ASes/DiaRCC/ASes_transito_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/ASes_imagenes/DiaRCC/AS_transito_"

#Se agrupa todos los datos de los distintos CSV en un unico dataframe
contador = 0

for version_rrc in rrc:

    if contador == 0:
	
        data_transito = pd.read_csv(url_transito+fecha+version_rrc+".csv",sep=",",dtype={"ASTransito": str})
        contador = 1
		
    else:
	
        data = pd.read_csv(url_transito+fecha+version_rrc+".csv",sep=",",dtype={"ASTransito": str})
        data_transito = data_transito.append(data,ignore_index = True)
		
print("Ya uní todos los dataframes")

#Obtengo lista de monitores distintos del dataframe y obtengo informacion de monitores y ASes relacionado con AS_PATH prepending
lista_monitores_transito = data_transito.Monitor.unique().tolist()

[diccionario_monitores_ASes_validos,diccionario_monitores_ASes_validos_ipv6,
 lista_prep_ipv4,lista_prep_ipv6,lista_porc_prep_ipv4,
 lista_porc_prep_ipv6,lista_porc_prep_siempre_ipv4,lista_porc_prep_siempre_ipv6,
 lista_porc_prep_nunca_ipv4,lista_porc_prep_nunca_ipv6] = informacion_general_monitores(lista_monitores_transito,data_transito)


#Representacion del numero de ASes distintos vistos por monitor IPv4
lista_ordenada_monitores_ASes_validos = list(diccionario_monitores_ASes_validos.values())
lista_ordenada_monitores_ASes_validos.sort()
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_monitores_ASes_validos,(10,5),bar_width,opacity,
                                        "Numero ASes vistos","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

#Representacion del numero de ASes distintos vistos por monitor IPv6
title = ""
lista_ordenada_monitores_ASes_validos_ipv6 = list(diccionario_monitores_ASes_validos_ipv6.values())
lista_ordenada_monitores_ASes_validos_ipv6.sort()
lista_ordenada_monitores_ASes_validos_ipv6 = eliminar_valor_lista_alto(lista_ordenada_monitores_ASes_validos_ipv6,4000)
num_imagen = representacion_1_figura_lista_ordenada(lista_ordenada_monitores_ASes_validos_ipv6,(10,5),bar_width,opacity,
                                        "Numero ASes vistos","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")
										
#Representacion del numero de ASes que realizan prepending (al menos una vez) distintos vistos por monitor IPv4 e IPv6
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_prep_ipv4,(10,5),bar_width,opacity,
                                        "Numero ASes vistos","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

lista_prep_ipv6 = eliminar_valor_lista_alto(lista_prep_ipv6,600)
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_prep_ipv6,(10,5),bar_width,opacity,
                                        "Numero ASes vistos","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Representacion del porcentaje de ASes que nunca realizan AS_PATH prepending por monitor para IPv4 e IPv6
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_nunca_ipv4,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_nunca_ipv6,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Representacion del porcentaje de ASes que realizan AS_PATH prepending por monitor para IPv4 e IPv6
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_ipv4,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_ipv6,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Representacion del porcentaje de ASes que  realizan AS_PATH prepending en todas las apariciones por monitor para IPv4 e IPv6
title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_siempre_ipv4,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv4")

title = ""
num_imagen = representacion_1_figura_lista_ordenada(lista_porc_prep_siempre_ipv6,(10,5),bar_width,opacity,
                                        "Porcentaje","Monitores",title,num_imagen,fecha,url_imagen,"IPv6")

#Representacion de en cuantos monitores distintos aparece el AStransito 
lista_distintos_monitores = data_transito.groupby("ASTransito").size().tolist()
contador_distintos_monitores_repeticiones = collections.Counter(lista_distintos_monitores)

title = ""
num_imagen = representacion_1_figura_contadores(contador_distintos_monitores_repeticiones,
            (10,5),"Numero ASes distintos","Monitores distintos",title,num_imagen,fecha,url_imagen)

#Obtencion de informacion relativa al AS y en cuantos monitores distintos realiza AS_PATH prepending alguna vez
[num_ASes,num_no_prepending,num_algunos_prepending,num_todos_prep,
 num_no_prepending_filt,num_algunos_prepending_filt,
 num_todos_prep_filt] = informacion_AStransito_prepending_cuantos_monitores(data_transito)

#Representacion de la distribucion/porcentaje de ASes que realizan AS_PATH prepending (alguna vez) en todos/ninguno/algunos de los monitores
#en los que tiene presencia
lista_info_final = [num_todos_prep,num_algunos_prepending,num_no_prepending,num_ASes]
labels_dicc = ["Todos", "Algunos",
               "Ninguno","Numero ASes totales"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')


lista_info_final_porcentaje = [num_todos_prep/num_ASes,num_algunos_prepending/num_ASes,num_no_prepending/num_ASes]
labels_dicc = ["Todos", "Algunos","Ninguno"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_porcentaje,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')

#Representacion de la distribucion/porcentaje de ASes (que aparecen en mas de 300 monitores distintos) 
#que realizan AS_PATH prepending (alguna vez) en todos/ninguno/algunos de los monitores
#en los que tiene presencia. 
num_ASes_filt = num_todos_prep_filt + num_algunos_prepending_filt + num_no_prepending_filt
lista_info_final_filtrado = [num_todos_prep_filt,num_algunos_prepending_filt,num_no_prepending_filt,num_ASes_filt]
labels_dicc = ["Todos", "Algunos",
               "Ninguno","Numero ASes totales"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_filtrado,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')

lista_info_final_porcentaje = [num_todos_prep_filt/num_ASes_filt,num_algunos_prepending_filt/num_ASes_filt,num_no_prepending_filt/num_ASes_filt]
labels_dicc = ["Todos", "Algunos","Ninguno"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_porcentaje,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')


#Representacion de la distribucion/porcentaje de ASes que realizan AS_PATH prepending (en todas sus apariciones) en todos/ninguno/algunos de los monitores
#en los que tiene presencia
[num_ASes,num_no_prepending,num_algunos_prepending,num_todos_prep,
 num_no_prepending_filt,num_algunos_prepending_filt,
 num_todos_prep_filt] = informacion_AStransito_prepending_siempre_cuantos_monitores(data_transito)

lista_info_final = [num_todos_prep,num_algunos_prepending,num_no_prepending,num_ASes]
labels_dicc = ["Todos", "Algunos",
               "Ninguno","Numero ASes totales"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')


lista_info_final_porcentaje = [num_todos_prep/num_ASes,num_algunos_prepending/num_ASes,num_no_prepending/num_ASes]
labels_dicc = ["Todos", "Algunos","Ninguno"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_porcentaje,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')

				
#Representacion de la distribucion/porcentaje de ASes (que aparecen en mas de 300 monitores distintos) 
#que realizan AS_PATH prepending (en todas sus apariciones) en todos/ninguno/algunos de los monitores
#en los que tiene presencia. 				
num_ASes_filt = num_todos_prep_filt + num_algunos_prepending_filt + num_no_prepending_filt
lista_info_final_filtrado = [num_todos_prep_filt,num_algunos_prepending_filt,num_no_prepending_filt,num_ASes_filt]
labels_dicc = ["Todos", "Algunos",
               "Ninguno","Numero ASes totales"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_filtrado,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')


lista_info_final_porcentaje = [num_todos_prep_filt/num_ASes_filt,num_algunos_prepending_filt/num_ASes_filt,num_no_prepending_filt/num_ASes_filt]
labels_dicc = ["Todos", "Algunos","Ninguno"]

title = ""
num_imagen = representacion_1_figura_lista(lista_info_final_porcentaje,labels_dicc,(10,5),"Numero ASes Transito distintos",
                "Monitor",title,num_imagen,fecha,url_imagen,bar_width,opacity,'vertical')

