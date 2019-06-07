#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs para un pequeño experimento de
prefijos base con longitud de prefijo 24.

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "Agrupacion_Prefijos_Mas_Especificos_long24" para todos los colectores de los que
se quiera obtener informacion.

IMPORTANTE2: Debe estar disponible la ruta "ResultadosCSV/Mas_Especificos_imagenes/DiaRCC/", ya que es donde se almacenan las imagenes.
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

'''
func:
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

'''-------    main     -------'''

#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8
num_imagen = 1

#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url_ipv4 = "ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv4_global_24_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/Mas_Especificos_imagenes/DiaRCC/Mas_Especificos_24_"

#Lectura del fichero y creacion de DataFrame
data_ipv4 = pd.read_csv(url_ipv4+fecha+".csv",sep=",")

#Se obtiene el numero de bases totales y numero de bases totales sobre los que se ha observado AS_PATH prepending
num_bases_totales = data_ipv4.BasesTotales.sum()
num_bases_totales_prep = data_ipv4.BasesTotalesPrep.sum()

#Representacion en diagrama circular del Numero de bases sin AS_PATH prepending y Numero de bases con AS_PATH prepending
lista_pie = [num_bases_totales-num_bases_totales_prep,num_bases_totales_prep]
labels_pie = ["Entradas de bases con longitud 24 sin prepending", "Entradas de bases con longitud 24 con prepending"]
title = ""
num_imagen = representacion_pie((10,6),lista_pie,labels_pie,"Leyenda de AS",title,num_imagen,fecha,url_imagen,"Entradas")
print("ok")