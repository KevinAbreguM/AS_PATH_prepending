#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa que emplea la informacion de prefijos mas especificos presente en ficheros CSV para cada colector. 
Se agrupa la informacion por AS que origina anuncios y se almacena con un formato mas sencillo de representar posteriormente en un fichero CSV.

IMPORTANTE: Para el comportamiento deseado debe haberse ejecutado el codigo de "obtencion_info_general" para todos los colectores de los que
se quiera obtener informacion.

Los resultados se almacenan en la ruta ResultadosCSV/Mas_Especificos/DiaRCC/
@author: kevin
"""

"""-----Librerias utilizadas -----"""

import sys, re;
import pandas as pd
from os import *
from pylab import *
import matplotlib.pyplot as plt
import collections
import socket
import random
import ast
from time import time

'''-------    FUNCIONES     -------'''

'''almacenar_diccionario_mas_especificos_final:
	Funcion que modifica el formato del diccionario (con agrupacion de toda la informacion de los distintos colectores)
		- Clave: El elemento AS origen (AS que origina tramas) 
		- Values: 1. Lista con los prefijos en formato de mascara IP.
				  2. Diccionario con informacion de apariciones y de veces que
				  realiza AS_PATH prepending
	A un formato:
		- Clave: El elemento AS origen (AS que origina tramas)
		- Values: 1. AS origen (Por arquitectura de DataFrames)
				  2. Numero de prefijos bases distintos
				  3. Numero de prefijos especificos distintos
				  4. Apariciones de prefijos bases totales
				  5. Apariciones de prefijos especificos totales
				  6. Numero de prefijos bases distintos sobre los que se observa AS_PATH prepending
				  7. Numero de prefijos especificos distintos sobre los que se observa AS_PATH prepending
				  8. Apariciones de prefijos bases  sobre los que se observa AS_PATH prepending
				  9. Apariciones de prefijos especificos  sobre los que se observa AS_PATH prepending
		
'''
def almacenar_diccionario_mas_especificos_final(dicc_ASOrigen_esp):

    dicc_ASOrigen_esp_final  = {}
	
	# Para cada AS origen realizo la conversion al formato de diccionario deseado
    for i,v in dicc_ASOrigen_esp.items():
		
		# Si el AS origen unicamente anuncia un prefijo, se sabe directamente que no es un prefijo especifico
        if len(v[0]) == 1:
			
			#Creo el diccionario indicando que no hay prefijos especificos y unicamente con informacion de prefijos base
            lista_aux = v[1].get(v[0][0])
            prep_aux = 0
			
			#Compruebo si se ha realizado AS_PATH prepending
            if lista_aux[0] > 0:
			
                prep_aux = 1
				
            dicc_ASOrigen_esp_final.update({i:[i,1,0,lista_aux[1],0,prep_aux,0,lista_aux[0],0]})
		
		# Si el AS origen  anuncia mas de un prefijo, hay que comprobar que prefijos son base y cuales más especificos (si los hay)
        else:
			
			#Ordeno la lista de mascaras para manejar primero las mascaras con longitud mas pequena (y asi asegurarme
			#que la primera eleccion no es un prefijo mas especifico)
            lista_mask = sorted(v[0],key=len)
			
			#variables de control de prefijos base/especificos y de AS_PATH prepending
            contador_especificos = 0
            lista_bases = []
            num_bases_totales = 0
            num_bases_totales_prep = 0
            num_esp_totales = 0
            num_esp_totales_prep = 0
            
            num_bases_unicos_prep = 0
            num_esp_unicos_prep = 0
			
			#Recorro la lista ordenada de mascaras
            for x in lista_mask:
				
				#La primera mascara siempre es un prefijo base (al ser la mas pequena) == La longitud de prefijo menor
                if x == lista_mask[0]:
				
                    lista_bases.append(x)
				
				#Si no es la primera mascara de la lista, compruebo si es un prefijo mas especifico
                else:
				
                    es_especifico = 0
					
					#Compruebo si la mascara actual, empieza exactamente igual que alguna mascara indicada como prefijo base.
					# Si coincide es un prefijo mas especifico y se anade a la lista de prefijos mas especificos
					# Si no coincide, es un prefijo base nuevo  y se anade a la lista de prefijos
                    for z in lista_bases:
						
                        if x.startswith(z):
						
                            contador_especificos=contador_especificos+1
                            es_especifico=1
							
                    if es_especifico==0:
					
                        lista_bases.append(x)
			
			#Una vez se ha distribuido el AS origen entre sus prefijos bases y especificos se obtiene la contribucion de cada mascara
            for z,k in v[1].items():
				
				#Si la mascara pertenece a la lista de prefijos base se anade su contribucion a este grupo.
                if z in lista_bases:
				
                    num_bases_totales = num_bases_totales+k[1]
                    num_bases_totales_prep = num_bases_totales_prep+k[0]
					
                    if k[0] > 0:
					
                        num_bases_unicos_prep = num_bases_unicos_prep + 1
				
				#Si la mascara pertenece a la lista de prefijos mas especificos se anade su contribucion a este grupo.
                else:
				
                    num_esp_totales = num_esp_totales + k[1]
                    num_esp_totales_prep = num_esp_totales_prep + k[0]
					
                    if k[0] > 0:
					
                        num_esp_unicos_prep = num_esp_unicos_prep + 1
        
            dicc_ASOrigen_esp_final.update({i:[i,len(lista_bases),contador_especificos
                ,num_bases_totales,num_esp_totales,num_bases_unicos_prep,num_esp_unicos_prep,
                num_bases_totales_prep,num_esp_totales_prep]})
				
    return dicc_ASOrigen_esp_final





'''-------    main     -------'''

#Ficheros CSV disponibles para esa fecha
rrc = ["_0","_1","_3","_4","_5","_6","_7","_10","_11","_12","_13","_14","_15","_16",
       "_18","_19","_20","_21"]
#Fecha de los ficheros CSV
fecha = "20180110-20180110"

#URLs donde se encuentran los ficheros CSV
url_mas_especificos = "ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv4_"
url_mas_especificos_ipv6 = "ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv6_"

start_time = time()

contador = 0

diccionario_completo = {}    
diccionario_completo_ipv6 = {}    

#Bucle que recorre cada colector con ficheros CSV disponibles
for version_rrc in rrc:
    
	#Lectura del fichero CSV para IPv4 e IPv6 de manera independiente
    data = pd.read_csv(url_mas_especificos+fecha+version_rrc+".csv",sep=",",dtype={"Unnamed: 0": str})
    data_ipv6 = pd.read_csv(url_mas_especificos_ipv6+fecha+version_rrc+".csv",sep=",",dtype={"Unnamed: 0": str})
    data.columns = ["ASOrigen","MascarasIP","DiccionariosIP"]
    data_ipv6.columns = ["ASOrigen","MascarasIP","DiccionariosIP"]
	
	#Obtengo las columnas del dataframe 
    dicc_ip = data.DiccionariosIP.tolist()
    lista_ASorigen = data.ASOrigen.tolist()
    
    dicc_ipv6 = data_ipv6.DiccionariosIP.tolist()
    lista_ASorigen_ipv6 = data_ipv6.ASOrigen.tolist()
    
	#Como la lectura de diccionarios no se realiza correctamente, se corrige con la funcion ast.literal
    lista_diccionarios = []
	
    for x in dicc_ip:
	
        lista_diccionarios.append(ast.literal_eval(x))
        
    lista_diccionarios_ipv6 = []
	
    for x in dicc_ipv6:
	
        lista_diccionarios_ipv6.append(ast.literal_eval(x))
		
	#Creo un diccionario con el formato adecuado AS origen: Lista de mascaras IP - Diccionario info Apariciones/Prepending
    diccionario_final = {}
    numero_elemento = 0
	
    for x in lista_diccionarios:
	
        diccionario_final.update({lista_ASorigen[numero_elemento]:[list(x.keys()),x]})
        numero_elemento = numero_elemento + 1
        
    diccionario_final_ipv6 = {}
    numero_elemento = 0
	
    for x in lista_diccionarios_ipv6:
	
        diccionario_final_ipv6.update({lista_ASorigen_ipv6[numero_elemento]:[list(x.keys()),x]})
        numero_elemento = numero_elemento + 1
    
	#Agrupo la informacion de todos los colectores en un unico diccionario (mismo procedimiento en IPv6)
	#Expandiendolo con cada nuevo colector procesado
    for j,k in diccionario_final.items():
	
        if not j in diccionario_completo:
		
            diccionario_completo.update({j:[k[0],k[1]]})
			
        else:
		
            lista_auxiliar_0 = diccionario_completo.get(j)[0]
            dicc_auxiliar = diccionario_completo.get(j)[1]
			
            for z in k[0]:
			
                if not z in lista_auxiliar_0:
				
                    lista_auxiliar_0.append(z)
					
            for i,v in k[1].items():
			
                if not i in dicc_auxiliar:
				
                    dicc_auxiliar.update({i:v})
					
                else:
				
                    lista_aux_dicc = dicc_auxiliar.get(i)
                    dicc_auxiliar.update({i:[lista_aux_dicc[0]+v[0],lista_aux_dicc[1]+v[1]]})
            
            diccionario_completo.update({j:[lista_auxiliar_0,dicc_auxiliar]})
    
    for j,k in diccionario_final_ipv6.items():
	
        if not j in diccionario_completo_ipv6:
		
            diccionario_completo_ipv6.update({j:[k[0],k[1]]})
			
        else:
		
            lista_auxiliar_0 = diccionario_completo_ipv6.get(j)[0]
            dicc_auxiliar = diccionario_completo_ipv6.get(j)[1]
			
            for z in k[0]:
			
                if not z in lista_auxiliar_0:
				
                    lista_auxiliar_0.append(z)
					
            for i,v in k[1].items():
			
                if not i in dicc_auxiliar:
				
                    dicc_auxiliar.update({i:v})
					
                else:
				
                    lista_aux_dicc = dicc_auxiliar.get(i)
                    dicc_auxiliar.update({i:[lista_aux_dicc[0]+v[0],lista_aux_dicc[1]+v[1]]})
            
            diccionario_completo_ipv6.update({j:[lista_auxiliar_0,dicc_auxiliar]})
			
    print("Estoy en RRC" + version_rrc)
    print(len(diccionario_completo))
    
#Modifico el formato de diccionario para facilitar su posterior procesamiento
dicc_ASOrigen_ipv4_final= almacenar_diccionario_mas_especificos_final(diccionario_completo)
dicc_ASOrigen_ipv6_final= almacenar_diccionario_mas_especificos_final(diccionario_completo_ipv6)

#Etiquetas del fichero CSV que se almacenará
labels_especificos = ["ASOrigen","BasesUnicos","EspecificosUnicos","BasesTotales","EspecificosTotales","BasesUnicosPrep",
          "EspecificosUnicosPrep","BasesTotalesPrep","EspecificosTotalesPrep"]

#Almacenamiento de los diccionarios en ficheros con formato CSV
dataframe_csv_mas_especificos_ipv4 = pd.DataFrame.from_dict(dicc_ASOrigen_ipv4_final,orient='index',columns = labels_especificos)
dataframe_csv_mas_especificos_ipv6 = pd.DataFrame.from_dict(dicc_ASOrigen_ipv6_final,orient='index',columns = labels_especificos)
dataframe_csv_mas_especificos_ipv4.to_csv("ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv4_global_" + fecha  +  "_2.csv",index=False)
dataframe_csv_mas_especificos_ipv6.to_csv("ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv6_global_" + fecha +  "_2.csv",index=False)



elapsed_time = time() - start_time

print("Tiempo de ejecucion: " + str(elapsed_time))