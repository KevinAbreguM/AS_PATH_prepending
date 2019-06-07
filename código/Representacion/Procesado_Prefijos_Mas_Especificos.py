#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codigo que procesa la informacion de los CSVs a nivel de prefijos mas especificos y 
realiza distintas funciones/agrupaciones para obtener distintas representaciones a este nivel

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "Agrupacion_Prefijos_Mas_Especificos" para todos los colectores de los que
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
def func(pct,allvals):

    absolute = int(pct/100.*np.sum(allvals))
	
    return "{:.2f}%\n({:d} ASes) ".format(pct,absolute)

'''-------    main     -------'''

#Variables para la representacion de imagenes
bar_width=0.35
opacity=0.8
num_imagen = 1

#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV tanto de IPv4 como de IPv6
url_ipv4 = "ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv4_global_"
url_ipv6 = "ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv6_global_"

#URL donde se almacenan las figuras
url_imagen = "ResultadosCSV/Mas_Especificos_imagenes/DiaRCC/Mas_Especificos_"

#Lectura de los ficheros CSV a dataframe
data_ipv4 = pd.read_csv(url_ipv4+fecha+".csv",sep=",",dtype={"ASOrigen": str})
data_ipv6 = pd.read_csv(url_ipv6+fecha+".csv",sep=",",dtype={"ASOrigen": str})

#Obtencion del numero de ASes que originan tramas para cada tipo de IP
numero_ASOrigen_ipv4 = len(data_ipv4)
numero_ASOrigen_ipv6 = len(data_ipv6)

#Obtencion de elementos de tipo contador con la columna de bases unicas
contador_bases_unicas_ipv4 = collections.Counter(data_ipv4["BasesUnicos"].tolist())
contador_bases_unicas_ipv6 = collections.Counter(data_ipv6["BasesUnicos"].tolist())

#Realizacion de mascaras para obtener dataframes distintos en funcion de si existe
#prefijos mas especificos o no.
#Se realiza para IPv4 y para IPv6 
mask_especificos_ipv4 = data_ipv4["EspecificosUnicos"] > 0
mask_especificos_ipv6 = data_ipv6["EspecificosUnicos"] > 0
mask_noespecificos_ipv4 = data_ipv4["EspecificosUnicos"] == 0
mask_noespecificos_ipv6 = data_ipv6["EspecificosUnicos"] == 0

#Aplicacion de las anteriores mascaras para obtener los distintos dataframes
data_noesp_ipv4 = data_ipv4[mask_noespecificos_ipv4]
data_noesp_ipv6 = data_ipv6[mask_noespecificos_ipv6]
data_esp_ipv4 = data_ipv4[mask_especificos_ipv4]
data_esp_ipv6 = data_ipv6[mask_especificos_ipv6]

#Obtencion de la cantidad de ASes origen que realizan la tecnica de prefijos mas especificos
numero_ASOrigen_con_esp_ipv4 = len(data_esp_ipv4)
numero_ASOrigen_con_esp_ipv6 = len(data_esp_ipv6)

#Representacion de figura con la distribucion de la cantidad de prefijos bases distintos para IPv4 e IPv6
#Se representa con un diagrama de barras
#Creacion de la figura de una fila y dos columnas
fig,ax = plt.subplots(nrows = 1, ncols = 2,figsize=(20,5))

#Se anade caracteristicas al primer elemento de la figura
ax[0].bar(contador_bases_unicas_ipv4.keys(),contador_bases_unicas_ipv4.values(),color='b')
ax[0].set_ylabel("Número ASes Origen")
ax[0].set_xlabel("Número prefijos bases distintos")
ax[0].set_title("")
ax[0].set_xlim(0,50)

#Se anade caracteristicas al segundo elemento de la figura
ax[1].bar(contador_bases_unicas_ipv6.keys(),contador_bases_unicas_ipv6.values(),color='y')
ax[1].set_ylabel("Número ASes Origen")
ax[1].set_xlabel("Número prefijos bases distintos")
ax[1].set_title("")
ax[1].set_xlim(0,23)

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con la distribucion ASes origen que realizan la tecnica de prefijos mas especificos o no para IPv4
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,5),subplot_kw = dict(aspect="equal"))

#Creacion de la lista con [ASes origen sin prefijos mas especificos, ASes origen con prefijos mas especificos]
lista_ip = [numero_ASOrigen_ipv4-numero_ASOrigen_con_esp_ipv4, numero_ASOrigen_con_esp_ipv4]
labels = ["ASes Origen sin específicos", "ASes Origen con específicos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

#Se almacena la figura en la URL indicada
savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con la distribucion ASes origen que realizan la tecnica de prefijos mas especificos o no para IPv6
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,5),subplot_kw = dict(aspect="equal"))

#Creacion de la lista con [ASes origen sin prefijos mas especificos, ASes origen con prefijos mas especificos]
lista_ip = [numero_ASOrigen_ipv6-numero_ASOrigen_con_esp_ipv6, numero_ASOrigen_con_esp_ipv6]
labels = ["ASes origen sin específicos", "ASes origen con específicos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

#Se almacena la figura en la URL indicada
savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Obtencion de elementos de tipo contador con la columna de bases especificas
contador_esp_unicas_ipv4 = collections.Counter(data_esp_ipv4["EspecificosUnicos"].tolist())
contador_esp_unicas_ipv6 = collections.Counter(data_esp_ipv6["EspecificosUnicos"].tolist())

#Representacion de figura con la distribucion de la cantidad de prefijos especificos distintos para IPv4 e IPv6
#Se representa con un diagrama de barras
#Creacion de la figura de una fila y dos columnas
fig,ax = plt.subplots(nrows = 1, ncols = 2,figsize=(20,5))

#Se anade caracteristicas al primer elemento de la figura
ax[0].bar(contador_esp_unicas_ipv4.keys(),contador_esp_unicas_ipv4.values(),color='b')
ax[0].set_ylabel("Número ASes Origen")
ax[0].set_xlabel("Número prefijos específicos distintos")
ax[0].set_title("")
ax[0].set_xlim(0,50)

#Se anade caracteristicas al segundo elemento de la figura
ax[1].bar(contador_esp_unicas_ipv6.keys(),contador_esp_unicas_ipv6.values(),color='y')
ax[1].set_ylabel("Número ASes Origen")
ax[1].set_xlabel("Número prefijos específicos distintos")
ax[1].set_title("")
ax[1].set_xlim(0,50)

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Obtencion del numero de ASes que no realizan la tecnica de prefijos mas especificos
numero_noesp_ipv4 = len(data_noesp_ipv4)
numero_noesp_ipv6 = len(data_noesp_ipv6)

#Creacion mascaras para comprobar si se realiza prepending en los prefijos mas especificas y obtencion dataframes
mask_noesp_noprep_ipv4 = data_noesp_ipv4["BasesUnicosPrep"] == 0
mask_noesp_noprep_ipv6 = data_noesp_ipv6["BasesUnicosPrep"] == 0
mask_noesp_siprep_ipv4 = data_noesp_ipv4["BasesUnicosPrep"] > 0
mask_noesp_siprep_ipv6 = data_noesp_ipv6["BasesUnicosPrep"] > 0

data_noesp_noprep_ipv4 = data_noesp_ipv4[mask_noesp_noprep_ipv4]
data_noesp_noprep_ipv6 = data_noesp_ipv6[mask_noesp_noprep_ipv6]
data_noesp_siprep_ipv4 = data_noesp_ipv4[mask_noesp_siprep_ipv4]
data_noesp_siprep_ipv6 = data_noesp_ipv6[mask_noesp_siprep_ipv6]

#Para ASes que no realizan la tecnica de prefijos mas especificas se obtiene su distribucion segun realizacion de AS_PATH prepending
#Comprobandose si el AS no realiza prepending, si el AS realiza prepending alguna vez, o si lo realiza siempre (A NIVEL DE bases distintos)
numero_noesp_noprep_ipv4 = len(data_noesp_noprep_ipv4)
numero_noesp_noprep_ipv6 = len(data_noesp_noprep_ipv6)

C = np.where((data_noesp_siprep_ipv4["BasesUnicos"] ==
                                       data_noesp_siprep_ipv4["BasesUnicosPrep"]),1,0)
    
numero_noesp_siprep_siempre_ipv4 = C.sum()
numero_noesp_siprep_algunos_ipv4 = len(C) - numero_noesp_siprep_siempre_ipv4

C = np.where((data_noesp_siprep_ipv6["BasesUnicos"] ==
                                       data_noesp_siprep_ipv6["BasesUnicosPrep"]),1,0)
    
numero_noesp_siprep_siempre_ipv6 = C.sum()
numero_noesp_siprep_algunos_ipv6 = len(C) - numero_noesp_siprep_siempre_ipv6


#Representacion de figura con  ASes origen que no realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv4
#A nivel de prefijos bases distintos
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv4, numero_noesp_siprep_algunos_ipv4,numero_noesp_siprep_siempre_ipv4]
labels = ["ASes Origen nunca hacen prepending", "ASes Origen hacen prepending en algunos prefijos","ASes Origen hacen prepending en todos sus prefijos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con  ASes origen que no realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv6
#A nivel de prefijos bases distintos
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv6, numero_noesp_siprep_algunos_ipv6,numero_noesp_siprep_siempre_ipv6]
labels = ["ASes Origen nunca hacen prepending", "ASes Origen hacen prepending en algunos prefijos","ASes Origen hacen prepending en todos sus prefijos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Para ASes que no realizan la tecnica de prefijos mas especificas se obtiene su distribucion segun realizacion de AS_PATH prepending
#Comprobandose si el AS no realiza prepending, si el AS realiza prepending alguna vez, o si lo realiza siempre (A NIVEL DE apariciones)
C = np.where((data_noesp_siprep_ipv4["BasesTotales"] ==
                                       data_noesp_siprep_ipv4["BasesTotalesPrep"]),1,0)
    
numero_noesp_siprep_total_ipv4 = C.sum()
numero_noesp_siprep_total_aveces_ipv4 = len(C) - numero_noesp_siprep_total_ipv4

C = np.where((data_noesp_siprep_ipv6["BasesTotales"] ==
                                       data_noesp_siprep_ipv6["BasesTotalesPrep"]),1,0)
    
numero_noesp_siprep_total_ipv6 = C.sum()
numero_noesp_siprep_total_aveces_ipv6 = len(C) - numero_noesp_siprep_total_ipv6

#Representacion de figura con ASes origen que no realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv4
#A nivel de apariciones 
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv4, numero_noesp_siprep_total_aveces_ipv4,numero_noesp_siprep_total_ipv4]
labels = ["ASes Origen nunca hacen prepending", "ASes Origen hacen prepending en algunos anuncios","ASes Origen hacen prepending en todos sus anuncios"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con ASes origen que no realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv6
#A nivel de apariciones 
#Se representa con un diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv6, numero_noesp_siprep_total_aveces_ipv6,numero_noesp_siprep_total_ipv6]
labels = ["ASes Origen nunca hacen prepending", "ASes Origen hacen prepending en algunos anuncios","ASes Origen hacen prepending en todos sus anuncios"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Creacion de mascaras para obtener si el AS origen que realiza la tecnica de prefijos mas especificos,
#realiza prepending en los prefijos base, en los prefijos especificos, en ninguno o en ambos.
#Posteriormente se forma el correspondiente DataFrame y se obtienen estadisticas de cada caso
mask_esp_prep_base_ipv4 = data_esp_ipv4["BasesUnicosPrep"] > 0 
mask_esp_prep_esp_ipv4 = data_esp_ipv4["EspecificosUnicosPrep"] > 0
mask_esp_noprep_base_ipv4 = data_esp_ipv4["BasesUnicosPrep"] == 0 
mask_esp_noprep_esp_ipv4 = data_esp_ipv4["EspecificosUnicosPrep"] == 0
mask_esp_prep_base_ipv6 = data_esp_ipv6["BasesUnicosPrep"] > 0 
mask_esp_prep_esp_ipv6 = data_esp_ipv6["EspecificosUnicosPrep"] > 0
mask_esp_noprep_base_ipv6 = data_esp_ipv6["BasesUnicosPrep"] == 0 
mask_esp_noprep_esp_ipv6 = data_esp_ipv6["EspecificosUnicosPrep"] == 0

data_esp_noprep_ipv4=data_esp_ipv4[mask_esp_noprep_base_ipv4 & mask_esp_noprep_esp_ipv4]
data_esp_prep_base_ipv4=data_esp_ipv4[mask_esp_prep_base_ipv4 & mask_esp_noprep_esp_ipv4]
data_esp_prep_esp_ipv4=data_esp_ipv4[mask_esp_prep_esp_ipv4 & mask_esp_noprep_base_ipv4]
data_esp_prep_ambos_ipv4 = data_esp_ipv4[mask_esp_prep_base_ipv4 & mask_esp_prep_esp_ipv4]
data_esp_noprep_ipv6=data_esp_ipv6[mask_esp_noprep_base_ipv6 & mask_esp_noprep_esp_ipv6]
data_esp_prep_base_ipv6=data_esp_ipv6[mask_esp_prep_base_ipv6 & mask_esp_noprep_esp_ipv6]
data_esp_prep_esp_ipv6=data_esp_ipv6[mask_esp_prep_esp_ipv6 & mask_esp_noprep_base_ipv6]
data_esp_prep_ambos_ipv6 = data_esp_ipv6[mask_esp_prep_base_ipv6 & mask_esp_prep_esp_ipv6]


numero_esp_noprep_ipv4 = len(data_esp_noprep_ipv4)
numero_esp_prep_base_ipv4 = len(data_esp_prep_base_ipv4)
numero_esp_prep_esp_ipv4 = len(data_esp_prep_esp_ipv4)
numero_esp_prep_ambos_ipv4 = len(data_esp_prep_ambos_ipv4)
numero_esp_noprep_ipv6 = len(data_esp_noprep_ipv6)
numero_esp_prep_base_ipv6 = len(data_esp_prep_base_ipv6)
numero_esp_prep_esp_ipv6 = len(data_esp_prep_esp_ipv6)
numero_esp_prep_ambos_ipv6 = len(data_esp_prep_ambos_ipv6)

#Representacion de figura con ASes origen que realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv4
#Se representa si se realiza el AS_PATH prepending unicamente en prefijos base, unicamente en prefijos mas especificos o en ambos tipos
#Representacion en diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_esp_noprep_ipv4, numero_esp_prep_base_ipv4,numero_esp_prep_esp_ipv4,numero_esp_prep_ambos_ipv4]
labels = ["ASes Origen nunca hacen prepending", "ASes origen hacen prepending únicamente en prefijo base","ASes origen hacen prepending unicamente en prefijos específicos",
          "ASes Origen hacen prepending tanto en prefijo base como en más específicos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con ASes origen que realizan la tecnica de prefijos mas especificos segun realizacion de prepending para IPv6
#Se representa si se realiza el AS_PATH prepending unicamente en prefijos base, unicamente en prefijos mas especificos o en ambos tipos
#Representacion en diagrama circular
fig,ax = plt.subplots(figsize = (10,6),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_esp_noprep_ipv6, numero_esp_prep_base_ipv6,numero_esp_prep_esp_ipv6,numero_esp_prep_ambos_ipv6]

labels = ["ASes Origen nunca hacen prepending", "ASes origen hacen prepending únicamente en prefijo base","ASes origen hacen prepending unicamente en prefijos específicos",
          "ASes Origen hacen prepending tanto en prefijo base como en más específicos"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1



#Representacion de figura con toda la informacion obtenida anteriormente para IPv4 en diagrama circular
fig,ax = plt.subplots(figsize = (15,10),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv4, numero_noesp_siprep_algunos_ipv4,numero_noesp_siprep_siempre_ipv4,numero_esp_prep_ambos_ipv4, numero_esp_prep_base_ipv4,numero_esp_prep_esp_ipv4,numero_esp_noprep_ipv4]

labels = ["ASes Origen sin específicos y que nunca hacen prepending", "ASes Origen sin específicos y que hacen prepending en algunos prefijos","ASes Origen sin específicos y que hacen prepending en todos sus prefijos",
          "ASes Origen con específicos y que hacen prepending tanto en prefijo base como en mas específicos", "ASes Origen con específicos y que hacen prepending unicamente en prefijo base","ASes Origen con específicos y que hacen prepending unicamente en prefijos específicos",
          "ASes Origen con específicos y que nunca hacen prepending"]

wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

#Representacion de figura con toda la informacion obtenida anteriormente para IPv6 en diagrama circular
fig,ax = plt.subplots(figsize = (15,12),subplot_kw = dict(aspect="equal"))

lista_ip = [numero_noesp_noprep_ipv6, numero_noesp_siprep_algunos_ipv6,numero_noesp_siprep_siempre_ipv6,numero_esp_prep_ambos_ipv6, numero_esp_prep_base_ipv6,numero_esp_prep_esp_ipv6,numero_esp_noprep_ipv6]


labels = ["ASes Origen sin específicos y que nunca hacen prepending", "ASes Origen sin específicos y que hacen prepending en algunos prefijos","ASes Origen sin específicos y que hacen prepending en todos sus prefijos",
          "ASes Origen con específicos y que hacen prepending tanto en prefijo base como en mas específicos", "ASes Origen con específicos y que hacen prepending unicamente en prefijo base","ASes Origen con específicos y que hacen prepending unicamente en prefijos específicos",
          "ASes Origen con específicos y que nunca hacen prepending"]


wedges,texts,autotexts = ax.pie(lista_ip,autopct=lambda pct: func(pct,lista_ip),textprops=dict(color="w"))
ax.legend(wedges,labels,title = "Leyenda",loc = "center left", bbox_to_anchor = (1,0,0.5,1))
plt.setp(autotexts,size=8,weight="bold")
ax.set_title("",fontsize=12,fontweight='bold')

savefig(url_imagen+fecha+"_" + str(num_imagen),bbox_inches = "tight")#1
num_imagen = num_imagen + 1

