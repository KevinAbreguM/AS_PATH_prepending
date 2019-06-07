#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa que procesa la informacion del colector indicado.
Se realizan experimentos a distintos niveles, y se obtiene caracteristicas de dicho nivel que se 
almacena en distintos ficheros CSV para posteriormente agruparlos/procesarlos/representarlos

Se debe indicar el colector del que se quiere obtener la informacion, actualmente se debe realizar cada colector
de manera individual, en un futuro se extiende a realizar de manera conjunta

IMPORTANTE: Las carpetas donde se almacenan los CSV deben ser creadas anteriormente a la prueba:
Por ejemplo: Las pruebas a nivel AS_PATH se almacenan en la ruta "ResultadosCSV/ASPATH/DiaRCC/", por lo tanto
esos directorios deben existir.
Y asi con todas las pruebas.
@author: kevin
"""

"""-----Librerias utilizadas -----"""

import sys, re;
from os import *
import pandas as pd
import math
from time import time
import socket
import collections
from binascii import hexlify

'''-------    FUNCIONES     -------'''


'''ip2bin_v6:
	Funcion que obtiene
	la mascara de red binaria de un prefijo IPv6 sin contar el rango
'''
def ip2bin_v6(ipv6_addr):

    ip = ipv6_addr.split("/")
    binary = bin(int(hexlify(socket.inet_pton(socket.AF_INET6, ip[0])),16))[2:].zfill(128)
	
    range = int(ip[1]) if '/' in ipv6_addr else None
	
    return binary[:range] if range else binary

'''ip2bin:
	Funcion que obtiene 
	la mascara de red binaria de un prefijo IPv4 sin contar el rango
'''
def ip2bin(ip):

    octets=map(int,ip.split("/")[0].split("."))
    binary='{0:08b}{1:08b}{2:08b}{3:08b}'.format(*octets)
	
    range = int(ip.split('/')[1]) if '/' in ip else None
	
    return binary[:range] if range else binary

'''informacion_diccionarios_mas_especificos:
	Funcion que almacena en un diccionario informacion de prefijos mas especificos.
	Se realiza para ambos tipos de IP por separado.
		- Clave: El elemento AS origen (AS que origina tramas)
		- Values: 1. Lista con los prefijos en formato de mascara IP.
				  2. Diccionario con informacion de apariciones y de veces que
				  realiza AS_PATH prepending
'''
def informacion_diccionarios_mas_especificos(dicc_ASOrigen_esp_ipv4,dicc_ASOrigen_esp_ipv6,
    tipo_prefijo,AS_origen,prefijo_total,prepending_origen):
	
    if tipo_prefijo == "IPv4":
        
		# Si no se ha creado el diccionario con ese AS_Origen como clave, entonces se crea
        if not AS_origen in dicc_ASOrigen_esp_ipv4:
            
            lista_auxiliar =[]
            lista_auxiliar.append(ip2bin(prefijo_total))
            dicc_prepending = {}
            dicc_prepending.update({ip2bin(prefijo_total):[prepending_origen,1]})
            dicc_ASOrigen_esp_ipv4.update({AS_origen:[lista_auxiliar,dicc_prepending]})
			
        # Si ya existia el diccionario con ese AS_origen como clave, se actualizan los valores
        else:
        
            dicc_auxiliar = dicc_ASOrigen_esp_ipv4.get(AS_origen)[1]
            lista_auxiliar = dicc_ASOrigen_esp_ipv4.get(AS_origen)[0]
                
            if not ip2bin(prefijo_total) in lista_auxiliar:
                
                lista_auxiliar.append(ip2bin(prefijo_total))
                dicc_auxiliar.update({ip2bin(prefijo_total):[prepending_origen,1]})
                dicc_ASOrigen_esp_ipv4.update({AS_origen:[lista_auxiliar,dicc_auxiliar]})
            
            else:
            
                lista_dicc = dicc_auxiliar.get(ip2bin(prefijo_total))
                lista_dicc[0] = lista_dicc[0]+prepending_origen
                lista_dicc[1] = lista_dicc[1]+1
                dicc_ASOrigen_esp_ipv4.update({AS_origen:[lista_auxiliar,dicc_auxiliar]})
    
    else:
    
		# Si no se ha creado el diccionario con ese AS_Origen como clave, entonces se crea
        if not AS_origen in dicc_ASOrigen_esp_ipv6:
        
            lista_auxiliar =[]
            lista_auxiliar.append(ip2bin_v6(prefijo_total))
            dicc_prepending = {}
            dicc_prepending.update({ip2bin_v6(prefijo_total):[prepending_origen,1]})
            dicc_ASOrigen_esp_ipv6.update({AS_origen:[lista_auxiliar,dicc_prepending]})
			
        # Si ya existia el diccionario con ese AS_origen como clave, se actualizan los valores
        else:
        
            dicc_auxiliar = dicc_ASOrigen_esp_ipv6.get(AS_origen)[1]
            lista_auxiliar = dicc_ASOrigen_esp_ipv6.get(AS_origen)[0]
                
            if not ip2bin_v6(prefijo_total) in lista_auxiliar:
                
                lista_auxiliar.append(ip2bin_v6(prefijo_total))
                dicc_auxiliar.update({ip2bin_v6(prefijo_total):[prepending_origen,1]})
                dicc_ASOrigen_esp_ipv6.update({AS_origen:[lista_auxiliar,dicc_auxiliar]})
            
            else:
            
                lista_dicc = dicc_auxiliar.get(ip2bin_v6(prefijo_total))
                lista_dicc[0] = lista_dicc[0]+prepending_origen
                lista_dicc[1] = lista_dicc[1]+1
                dicc_ASOrigen_esp_ipv6.update({AS_origen:[lista_auxiliar,dicc_auxiliar]})
    
    return [dicc_ASOrigen_esp_ipv4,dicc_ASOrigen_esp_ipv6]

	
'''almacenar_diccionarios_longitudes_prefijo:
	Funcion que almacena en diccionarios informacion relativa a las longitudes de prefijo.
	Se realiza para ambos tipos de IP por separado.
	Se realiza una prueba teniendo en cuenta el monitor, otra teniendo en cuenta la longitud de AS_PATH,
	y otra de manera global.
		- Clave: El elemento de longitud de prefijo (OPCIONAL: Se anade tambien el monitor como parte de la clave)
				(OPCIONAL 2: Se anade tambien como clave la longitud de AS_PATH)
		- Values: 1. Longitud de prefijo + monitor <- (simplemente por arquitectura de diseno se repite la clave como value)
				  2. Apariciones de prepending para esa longitud de prefijo
				  3. Apariciones totales de la longitud
'''
def almacenar_diccionarios_longitudes_prefijo(diccionario_longitudes_monitores,diccionario_longitudes_total_long_ipv6,
                                              diccionario_longitudes_total_ipv6,diccionario_longitudes_total_long,
                                              diccionario_longitudes_total,monitor,prefijo_total,prepending,
                                              tipo_prefijo,longitud_aspath):
    # Se obtiene la longitud de prefijo
    prefijo = prefijo_total.split("/")
	
	# Si ya existia el diccionario con ese monitor + longitud de prefijo como clave, se actualizan los valores
	# de prepending y de apariciones totales
    if str(monitor)+"/"+prefijo[1] in diccionario_longitudes_monitores:
        
        lista_auxiliar = diccionario_longitudes_monitores.get(str(monitor)+"/"+prefijo[1])
        diccionario_longitudes_monitores.update({str(monitor)+"/"+prefijo[1]:[lista_auxiliar[0],
            lista_auxiliar[1],lista_auxiliar[2]+prepending,lista_auxiliar[3]+1]})

	# Si no se ha creado el diccionario con ese monitor + longitud de prefijo como clave, entonces se crea
    else:
        
        diccionario_longitudes_monitores.update({str(monitor)+"/"+prefijo[1]:[monitor,
            prefijo[1],prepending,1]})
    
	# Se separa las pruebas de longitudes de prefijo en funcion de si el prefijo anunciado es de tipo IPv4 o IPv6
    if tipo_prefijo == "IPv6":
        
		# Si ya existia el diccionario con esa longitud de prefijo + longitud de AS_PATH como clave, se actualizan los valores
        if prefijo[1]+"/"+str(longitud_aspath) in diccionario_longitudes_total_long_ipv6:
        
            lista_auxiliar = diccionario_longitudes_total_long_ipv6.get(prefijo[1]+"/"+str(longitud_aspath))
            diccionario_longitudes_total_long_ipv6.update({prefijo[1]+"/"+str(longitud_aspath):
                [lista_auxiliar[0],lista_auxiliar[1],lista_auxiliar[2]+prepending,lista_auxiliar[3]+1]})
		
		# Si no se ha creado el diccionario con esa longitud de prefijo + longitud de AS_PATH como clave, entonces se crea
        else:
            
            diccionario_longitudes_total_long_ipv6.update({prefijo[1]+"/"+str(longitud_aspath):
                [longitud_aspath,prefijo[1],prepending,1]})
         
		# Si ya existia el diccionario con esa longitud de prefijo como clave, se actualizan los valores
        if prefijo[1] in diccionario_longitudes_total_ipv6:
            
            lista_auxiliar = diccionario_longitudes_total_ipv6.get(prefijo[1])
            diccionario_longitudes_total_ipv6.update({prefijo[1]:[lista_auxiliar[0],
                lista_auxiliar[1]+prepending,lista_auxiliar[2]+1]})
		# Si no se ha creado el diccionario con esa longitud de prefijo como clave, entonces se crea
        else:
            
            diccionario_longitudes_total_ipv6.update({prefijo[1]:[prefijo[1],
                prepending,1]})
    else:
	
        # Si ya existia el diccionario con esa longitud de prefijo + longitud de AS_PATH como clave, se actualizan los valores
        if prefijo[1]+"/"+str(longitud_aspath) in diccionario_longitudes_total_long:
            
            lista_auxiliar = diccionario_longitudes_total_long.get(prefijo[1]+"/"+str(longitud_aspath))
            diccionario_longitudes_total_long.update({prefijo[1]+"/"+str(longitud_aspath):
                [lista_auxiliar[0],lista_auxiliar[1],lista_auxiliar[2]+prepending,lista_auxiliar[3]+1]})
        
		# Si no se ha creado el diccionario con esa longitud de prefijo + longitud de AS_PATH como clave, entonces se crea
        else:
            
            diccionario_longitudes_total_long.update({prefijo[1]+"/"+str(longitud_aspath):
                [longitud_aspath,prefijo[1],prepending,1]})
        
		# Si ya existia el diccionario con esa longitud de prefijo como clave, se actualizan los valores
        if prefijo[1] in diccionario_longitudes_total:
            
            lista_auxiliar = diccionario_longitudes_total.get(prefijo[1])
            diccionario_longitudes_total.update({prefijo[1]:[lista_auxiliar[0],
                lista_auxiliar[1]+prepending,lista_auxiliar[2]+1]})
        
		# Si no se ha creado el diccionario con esa longitud de prefijo como clave, entonces se crea
        else:
            
            diccionario_longitudes_total.update({prefijo[1]:[prefijo[1],
                prepending,1]})
				
    return [diccionario_longitudes_monitores,diccionario_longitudes_total_long_ipv6,
            diccionario_longitudes_total_ipv6,diccionario_longitudes_total_long,
            diccionario_longitudes_total]
	
'''almacenar_dicc_ASPATHs_final:
	Funcion que modifica el formato del diccionario de AS_PATHs pasado como argumento para obtener informacion más relevanteç
	del mismo, evitando que se almacene informacion innecesaria  en el fichero CSV correspondiente.
	
'''	
def almacenar_dicc_ASPATHs_final(dicc_ASPATHs):
    
    dicc_ASPATHs_final = {}
    
    for i,v in dicc_ASPATHs.items():
        
        dicc_ASPATHs_final.update({i:[v[0],len(v[1]),v[2],v[3],v[4],v[5],v[6],v[7],v[8],v[9],len(v[10]),v[11]]})
    
    return dicc_ASPATHs_final

'''almacenar_dicc_ASPATHs:
	Funcion que almacena en un diccionario informacion relativa al atributo AS_PATH
		- Clave: Atributo AS_PATH.
		- Values: 1. Atributo AS_PATH (por arquitectura de diseno se repite la clave como value)
				  2. Lista de prefijos distintos
				  3. Binario sobre si realiza prepending o no
				  4. Apariciones totales del AS_PATH
				  5. Numero de ASes haciendo AS_PATH prepending
				  6. Repeticion mas alta
				  7. Lista de ASes que hacen AS_PATH prepending
				  8. Distancia de los ASes que hacen AS_PATH prepending al origen
				  9. Numero de prefijos anunciados IPv4
				  10. Numero de prefijos anunciados IPv6
				  11. Monitores distintos en los que aparece el AS_PATH
				  12. Longitud de AS_PATH
'''
def almacenar_dicc_ASPATHs(dicc_ASPATHs,data_aspath,prefijo_total,prepending,repeticiones,valor_mas_alto_prep,
                           lista_ASes_prep,lista_ASes_prep_dist,tipo_prefijo_ipv4,tipo_prefijo_ipv6,monitor,longitud_aspath):
    
	#Se obtiene el prefijo anunciado sin la longitud de prefijo
    prefijo = prefijo_total.split("/")
    
	# Si no se ha creado el diccionario con ese AS_PATH como clave, entonces se crea
    if not data_aspath in dicc_ASPATHs:
        
        dicc_ASPATHs.update({data_aspath: [data_aspath,[prefijo[0]],
            prepending,1,repeticiones,valor_mas_alto_prep,lista_ASes_prep,
            lista_ASes_prep_dist,tipo_prefijo_ipv4,tipo_prefijo_ipv6,[str(monitor)],longitud_aspath]})
    
	# Si  se ha creado el diccionario con ese AS_PATH como clave, se actualizan los valores
    else:
    
        lista_auxiliar = dicc_ASPATHs.get(data_aspath)
        lista_auxiliar_2 = dicc_ASPATHs.get(data_aspath)[1]
        lista_auxiliar_3 = dicc_ASPATHs.get(data_aspath)[10]
        
		#Compruebo si el prefijo ya habia sido anadido previamente
        if not prefijo[0] in lista_auxiliar_2:
        
            lista_auxiliar_2.append(prefijo[0])
			
        # Compruebo si el monitor ya ha sido anadido 
        if not str(monitor) in lista_auxiliar_3:
            
            lista_auxiliar_3.append(str(monitor))
            
        dicc_ASPATHs.update({data_aspath:[lista_auxiliar[0],lista_auxiliar_2,
            lista_auxiliar[2],lista_auxiliar[3]+1,lista_auxiliar[4],lista_auxiliar[5],
            lista_auxiliar[6],lista_auxiliar[7],lista_auxiliar[8]+tipo_prefijo_ipv4,
            lista_auxiliar[9]+tipo_prefijo_ipv6,lista_auxiliar_3,lista_auxiliar[11]]})
    
    return dicc_ASPATHs

'''lista_aspaths_eliminando_repeticiones:
	Funcion que devuelve la lista del atributo AS_PATH quitando las repeticiones de AS_PATH prepending '''
def lista_aspaths_eliminando_repeticiones(data_aspath):
    
    lista_aspath_unico = []
	
    for x in data_aspath:
	
        if not x in lista_aspath_unico:
		
            lista_aspath_unico.append(x)
			
    return lista_aspath_unico

'''almacenar_diccionario_transito:
	Funcion que almacena en un diccionario informacion de ASes de transito por monitor.
	Es decir, ASes que no  originan rutas ni son el propio monitor.
		- Clave: Monitor + AS_transito
		- Values: 1. Monitor (por arquitectura de diseno se repite la clave como value)
				  2. AS transito (por arquitectura de diseno se repite la clave como value)
				  3. Veces que se realiza AS_PATH prepending
				  4. Apariciones totales del AS_transito
'''
	
def almacenar_diccionario_transito(diccionario_transito,valor,repeticion,ASMonitor,AS_origen,monitor):
    
	# Compruebo que el AS (valor) no sea el monitor
    if ASMonitor != valor:
        
		# El AS realiza AS_PATH prepending al tener mas de una repeticion
        if repeticion > 1:
            
			#Compruebo que el AS no sea el AS de origen
            if str(valor) != AS_origen:
                
				# Si no se ha creado el diccionario con ese AS + monitor como clave, entonces se crea
                if not str(monitor) + "," + valor in diccionario_transito:
                            
                    diccionario_transito.update({str(monitor)+","+valor:
                        [monitor,valor,1,1]})
						
				# Si se ha creado el diccionario con ese AS + monitor como clave, entonces se actualizan los valores
                else:
                    
                    lista_transito = diccionario_transito.get(str(monitor)+","+valor)
                    diccionario_transito.update({str(monitor)+","+valor: [lista_transito[0],
                            lista_transito[1],lista_transito[2]+1,lista_transito[3]+1]})

		# El AS no realiza AS_PATH prepending al tener mas una unica repeticion

        else:
            
			#Compruebo que el AS no sea el AS de origen
            if str(valor) != AS_origen:
			
				# Si no se ha creado el diccionario con ese AS + monitor como clave, entonces se crea
                if not str(monitor) + "," + valor in diccionario_transito:
                    diccionario_transito.update({str(monitor)+","+valor:
                        [monitor,valor,0,1]})
						
				# Si se ha creado el diccionario con ese AS + monitor como clave, entonces se actualizan los valores
                else:
                    lista_transito = diccionario_transito.get(str(monitor)+","+valor)
                    diccionario_transito.update({str(monitor)+","+valor: [lista_transito[0],
                                lista_transito[1],lista_transito[2],lista_transito[3]+1]})

    return diccionario_transito


'''almacenar_diccionario_origen
	Funcion que almacena en un diccionario informacion de ASes de origen por monitor.
	Es decir, ASes que originan rutas para anuncios de prefijos.
		- Clave: Monitor + AS_origen
		- Values: 1. Monitor (por arquitectura de diseno se repite la clave como value)
				  2. AS transito (por arquitectura de diseno se repite la clave como value)
				  3. Veces que se realiza AS_PATH prepending
				  4. Apariciones totales del AS_origen

'''

def almacenar_diccionario_origen(diccionario_origen,monitor,AS_origen,prepending_origen):
    
	# Si no se ha creado el diccionario con ese AS + monitor como clave, entonces se crea
    if not str(monitor)+","+AS_origen in diccionario_origen:
        
            diccionario_origen.update({str(monitor)+","+AS_origen: [monitor,AS_origen,prepending_origen,1]})
	
	# Si se ha creado el diccionario con ese AS + monitor como clave, entonces se actualizan los valores
    else:
        
        lista_origen = diccionario_origen.get(str(monitor)+","+AS_origen)
        diccionario_origen.update({str(monitor)+","+AS_origen:[lista_origen[0],
            lista_origen[1],lista_origen[2]+prepending_origen,lista_origen[3]+1]})
    
    return diccionario_origen

'''almacenar_dicc_monitor_prefijo_vecino
	Funcion que almacena en un diccionario informacion relativa a prefijos anunciados + ASes vecinos por monitor.
		- Clave: Monitor + Prefijo anunciado + AS vecino del monitor
		- Values: 1. Monitor (por arquitectura de diseno se repite la clave como value)
				  2. Prefijo anunciado (por arquitectura de diseno se repite la clave como value)
				  3. AS vecino (por arquitectura de diseno se repite la clave como value)
				  4. Veces que se realiza AS_PATH prepending
				  5. Numero de apariciones totales del par (prefijo + AS vecino) por cada monitor
				  6. Lista de ASes que hacen AS_PATH prepending
				  7. Prefijo sin la longitud de prefijo.
				  8. Longitud de prefijo.
				  9. Numero de veces que se anuncia un prefijo IPv4.
				  10. Numero de veces que se anuncia un prefijo IPv6

'''

def almacenar_dicc_monitor_prefijo_vecino(dicc_monitor_pref_vecinos,monitor,prefijo_total,vecino,lista_prepending,
                                          prepending,tipo_prefijo):
										  
    #Comprobacion del tipo de prefijo (IPv4 o IPv6)
    es_pref_ipv4 = 0
    es_pref_ipv6 = 0
    
    if tipo_prefijo == "IPv4":
	
        es_pref_ipv4 = 1
		
    else:
	
        es_pref_ipv6 = 1
        
    prefijo = prefijo_total.split("/")
	
	# Si se ha creado el diccionario con ese monitor + prefijo + vecino como clave, entonces se actualizan valores
    if str(monitor)+"/"+prefijo_total+"/"+vecino in dicc_monitor_pref_vecinos:
        
		#Obtengo valores existentes para actualizarlos.
        lista_auxiliar = dicc_monitor_pref_vecinos.get(str(monitor)+"/"+prefijo_total+"/"+vecino)
        lista_prepending_aux = dicc_monitor_pref_vecinos.get(str(monitor)+"/"+prefijo_total+"/"+vecino)[5]
        lista_prepending_aux.extend(lista_prepending)
		
        dicc_monitor_pref_vecinos.update({str(monitor)+"/"+prefijo_total+"/"+vecino:[lista_auxiliar[0],
            lista_auxiliar[1],lista_auxiliar[2],lista_auxiliar[3]+prepending,
            lista_auxiliar[4]+1,lista_prepending_aux,lista_auxiliar[6],lista_auxiliar[7],lista_auxiliar[8]+es_pref_ipv4,
            lista_auxiliar[9]+es_pref_ipv6]})
	
	# Si no se ha creado el diccionario con ese monitor + prefijo + vecino como clave, entonces se crea
    else:
        
        dicc_monitor_pref_vecinos.update({str(monitor)+"/"+prefijo_total+"/"+vecino:[monitor,
            prefijo_total,vecino,prepending,1,lista_prepending,prefijo[0],prefijo[1],es_pref_ipv4,es_pref_ipv6]})
    
    return dicc_monitor_pref_vecinos

'''almacenar_dicc_pref_vecinos
	Funcion que almacena en un diccionario informacion relativa a prefijos anunciados + ASes vecinos.
		- Clave: Prefijo anunciado + AS vecino del monitor
		- Values: 1. Prefijo anunciado (por arquitectura de diseno se repite la clave como value)
				  2. AS vecino (por arquitectura de diseno se repite la clave como value)
				  3. Veces que se realiza AS_PATH prepending
				  4. Numero de apariciones totales del par (prefijo + AS vecino) 
				  5. Lista de ASes que hacen AS_PATH prepending
				  6. Prefijo sin la longitud de prefijo.
				  7. Longitud de prefijo.
				  8. Numero de veces que se anuncia un prefijo IPv4.
				  9. Numero de veces que se anuncia un prefijo IPv6
'''

def almacenar_dicc_pref_vecinos(dicc_pref_vecinos,prefijo_total,vecino,lista_prepending,prepending,
                                tipo_prefijo):
								
    #Comprobacion del tipo de prefijo (IPv4 o IPv6)
    es_pref_ipv4 = 0
    es_pref_ipv6 = 0
    
    if tipo_prefijo == "IPv4":
	
        es_pref_ipv4 = 1
		
    else:
	
        es_pref_ipv6 = 1
        
    prefijo = prefijo_total.split("/")

	# Si se ha creado el diccionario con ese prefijo + vecino como clave, entonces se actualizan valores
    if prefijo_total+"/"+vecino in dicc_pref_vecinos:
                
        lista_auxiliar = dicc_pref_vecinos.get(prefijo_total+"/"+vecino)
        lista_prepending_aux = dicc_pref_vecinos.get(prefijo_total+"/"+vecino)[4]
        lista_prepending_aux.extend(lista_prepending)
		
        dicc_pref_vecinos.update({prefijo_total+"/"+vecino:[lista_auxiliar[0],
            lista_auxiliar[1],lista_auxiliar[2]+prepending,lista_auxiliar[3]+1,
            lista_prepending_aux,lista_auxiliar[5],lista_auxiliar[6],lista_auxiliar[7]+es_pref_ipv4,
            lista_auxiliar[8]+es_pref_ipv6]})
    
	# Si no se ha creado el diccionario con ese prefijo + vecino como clave, entonces se crea
    else:
            
        dicc_pref_vecinos.update({prefijo_total+"/"+vecino:[
            prefijo_total,vecino,prepending,1,lista_prepending,prefijo[0],prefijo[1],es_pref_ipv4,es_pref_ipv6]})

    return dicc_pref_vecinos


'''obtener_vecino:
	Funcion que devuelve (en caso de existir) el AS vecino del monitor.
'''
def obtener_vecino(data_aspath):
    
    prepending_origen = 0
    AS_origen = data_aspath[len(data_aspath)-1]
	
    if len(data_aspath) > 1:
	
        vecino = data_aspath[1]
		
        if AS_origen == data_aspath[len(data_aspath)-2]:
		
                prepending_origen = 1
				
    else:
	
        vecino = "-1"    
		
    return [vecino,prepending_origen]

'''tipo_ip:
	Funcion que devuelve un string indicando el tipo de prefijo (IPv4 o IPv6)
'''
def tipo_ip(prefijo_total):

    prefijo = prefijo_total.split("/")
	
    try:
	
        socket.inet_aton(prefijo[0])
        tipo_prefijo = "IPv4"
            
    except socket.error:
	
        tipo_prefijo = "IPv6"
		
    return tipo_prefijo
    
'''-------    main     -------'''


#Fechas de inicio y fin del analisis (para extender pruebas en un futuro a rangos superiores a un dia)
date_start = '20180110';
date_end = '20180110';


#Inicio la variable tiempo para comprobar cuanto tarda en realizarse el analisis.
start_time = time()

#Creacion lista de RRCs
rrcs = []

#Se indica el colector o rango de colectores a analizar
#Inicialmente pensado para colectores independientemente, aunque con ligeros cambios se puede escalar a varios colectores
#Por lo que hay que indicar el colector uno a uno
#La lista de colectores validos es: [0,1,3,4,5,6,7,10,11,12,
#13,14,15,16,18,19,20,21]
#Por ejemplo range (6,7) indica que se va a analizar el colector 6
rango_rrcs_analizar = range(6,7)


for contador in rango_rrcs_analizar:
	
	if contador < 10:
	
		if not contador == 2:
		
			rrcs.append("rrc0" + str(contador) + ".ripe")
			
	else:
	
		rrcs.append("rrc" + str(contador) + ".ripe")

# Fecha de analisis
fecha = '20180110'

#Nombres de las columnas leidas del TXT
column_names = ['RRC','AvsW','IPMonitor','ASMonitor','AnnouncedPrefix','longPrefix',\
            'IPType','ASPATH','Neighbor','COMMUNITIES'];
 
#Eliminacion columnas no importantes para este analisis 
column_drop = ['longPrefix', 'Neighbor']


#Creo un dataframe con las columnas del TXT
dataframe_all = pd.DataFrame([], columns=column_names)

#Ruta donde se encuentran el DataFrame con informacion del colector (TXT)
url = "/srv/agarcia/TFM-BGP/DATA_TXT/General/"

elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))

#Obtencion DataFrame con la informacion del colector (escalable a varios colectores) 
for rrc in rrcs:

    print(rrc)
    url_file = url+rrc+'_'+fecha+'.txt'
    data = pd.read_csv(url_file, sep='|',header=None, names=column_names, dtype={"Neighbor": object});
    dataframe_all = dataframe_all.append(data,ignore_index=True,sort=True)

dataframe_all = dataframe_all.drop(columns = column_drop)  

print("Comienzo la ejecucion, ya tengo el bigdataframe creado")
elapsed_time = time() - start_time
print("Tiempo de ejecucion: " + str(elapsed_time))



#Diccionarios con informacion de prefijos + vecinos (y monitores)
dicc_pref_vecinos= {}
dicc_monitor_pref_vecinos = {}

#Diccionarios con informacion de ASes de origen y transito
diccionario_origen = {}
diccionario_transito = {}

#Diccionario con informacion de ASPATH
dicc_ASPATHs = {}

#Diccionarios con informacion sobre la longitud total, con y sin monitores
#y dividida por tipo de IP, y con la longitud de AS_PATH
diccionario_longitudes_total = {}
diccionario_longitudes_total_ipv6 = {}
diccionario_longitudes_monitores = {}
diccionario_longitudes_total_long = {}
diccionario_longitudes_total_long_ipv6 = {}

#diccionarios de informacion de prefijos mas especificos
dicc_ASOrigen_esp_ipv4 = {}
dicc_ASOrigen_esp_ipv6 = {}
print("Ya tengo los archivos procedo a manipularlos")

#Bucle que recorre todos los monitores existentes en el dataframe y crea una mascara para cada uno de ellos
#Obteniendo distintos tipos de informacion que se almacenan en los diccionarios
for monitor in dataframe_all["IPMonitor"].unique():
	
	#Aplico la mascara del monitor del bucle al dataframe
    mask_monitor = dataframe_all["IPMonitor"] == monitor
    mask_AvsW = dataframe_all["AvsW"] != "W"
    mask_AvsW_2 = dataframe_all["AvsW"] != "STATE"
    df_anuncios = dataframe_all[mask_monitor & mask_AvsW & mask_AvsW_2]
    
    #Aplico el umbral para obtener informacion de los monitores proveedores
    #200.000 para IPv4 y 20.000 para IPv6
    try:
        socket.inet_aton(monitor)
        umbral_monitor = 200000
	
    except socket.error:

        umbral_monitor = 20000
    
	#Si se supera el umbral procedo a obtener la informacion
    if len(df_anuncios.AnnouncedPrefix.unique()) > umbral_monitor:
	
		#Variables para desplazarse a traves del dataframe
        numero_elementos = df_anuncios.index
        numero_elemento = 0
		
        # Obtencion de los prefijos anunciados del monitor 
        for prefijo_total in df_anuncios["AnnouncedPrefix"]:
		
			#Obtencion del tipo de prefijo (IPv4 o IPv6)
            tipo_prefijo = tipo_ip(prefijo_total)
			
            tipo_prefijo_ipv4 = 0
            tipo_prefijo_ipv6 = 0
			
            if tipo_prefijo == "IPv4":
				
                tipo_prefijo_ipv4 = 1
            else:
				
                tipo_prefijo_ipv6 = 1
			
			# Obtengo el AS_PATH del elemento que se esta analizando en el bucle
            data_aspath = str(df_anuncios["ASPATH"].loc[numero_elementos[numero_elemento]])
            data_aspath_completo = str(df_anuncios["ASPATH"].loc[numero_elementos[numero_elemento]])
			
            data_aspath = data_aspath.split(" ")
			
            #AS monitor
            ASMonitor = data_aspath[0]
			
            #AS origen del anuncio
            AS_origen = data_aspath[len(data_aspath)-1]
			
            #Variable para controlar los prefijos agregados
            prefijo_agregado = 0
			
            #Compruebo si hay prefijos agregados (nunca manejo los prefijos agregados)
            if len(AS_origen.split("{")) > 1:
				
                prefijo_agregado = 1
				
            if prefijo_agregado == 0:
				
                prepending_origen = 0
				
				#Obtengo el AS vecino y si se realiza AS_PATH prepending en el origen
                [vecino,prepending_origen] = obtener_vecino(data_aspath)
				
				#Obtengo informacion a nivel AS_origen
                diccionario_origen = almacenar_diccionario_origen(diccionario_origen,monitor,AS_origen,prepending_origen)
				
				#Obtengo la longitud de AS_PATH sin contar las repeticiones de AS_PATH prepending
                lista_aspath_unico = lista_aspaths_eliminando_repeticiones(data_aspath)
                longitud_aspath = len(lista_aspath_unico)
		
				#Utilizo elemento contador para determinar caracteristicas de AS_PATH prepending
                contador_repeticiones = collections.Counter(data_aspath)
				
				#Variables de AS_PATH prepending
                prepending = 0
                repeticiones = 0
                valor_mas_alto_prep = 0
                lista_ASes_prep  = []
                lista_ASes_prep_dist = []
				
                #Obtengo el AS que hace prepending y el numero de repeticiones (en caso de existir)
                # y distintas caracteristicas relevantes
                for valor, repeticion in contador_repeticiones.items():
				
                    if repeticion > 1:
					
                        prepending = 1
                        repeticiones = repeticiones + 1
                        lista_ASes_prep.append(valor)
                        lista_ASes_prep_dist.append(len(lista_aspath_unico)-1-lista_aspath_unico.index(valor))
						
                        if repeticion > valor_mas_alto_prep:
						
                            valor_mas_alto_prep = repeticion
                    # Almaceno informacion de ASes transito
                    diccionario_transito = almacenar_diccionario_transito(diccionario_transito,
												valor,repeticion,ASMonitor,AS_origen,monitor)
				
				#En caso de existir prepending obtengo informacion sobre el AS que mayor secuencia de repeticion aplica
                lista_prepending = []
				
                if prepending == 1:
                    asPrepending = (contador_repeticiones.most_common(1))[0][0]
                    lista_prepending.append(asPrepending)
					
				#Obtengo distintas informaciones relevantes y lo almaceno en diccionarios
                dicc_pref_vecinos = almacenar_dicc_pref_vecinos(dicc_pref_vecinos,prefijo_total,vecino,lista_prepending,prepending,
										tipo_prefijo)
                dicc_monitor_pref_vecinos = almacenar_dicc_monitor_prefijo_vecino(dicc_monitor_pref_vecinos,monitor,prefijo_total,vecino,lista_prepending,
												  prepending,tipo_prefijo)
                dicc_ASPATHs = almacenar_dicc_ASPATHs(dicc_ASPATHs,data_aspath_completo,prefijo_total,prepending,repeticiones,valor_mas_alto_prep,
								   lista_ASes_prep,lista_ASes_prep_dist,tipo_prefijo_ipv4,tipo_prefijo_ipv6,monitor,longitud_aspath)
				
				
                [diccionario_longitudes_monitores,diccionario_longitudes_total_long_ipv6,
                 diccionario_longitudes_total_ipv6,diccionario_longitudes_total_long,
                 diccionario_longitudes_total] = almacenar_diccionarios_longitudes_prefijo(diccionario_longitudes_monitores,diccionario_longitudes_total_long_ipv6,
					diccionario_longitudes_total_ipv6,diccionario_longitudes_total_long,
					diccionario_longitudes_total,monitor,prefijo_total,prepending,
					tipo_prefijo,longitud_aspath)
				
                [dicc_ASOrigen_esp_ipv4,dicc_ASOrigen_esp_ipv6] = informacion_diccionarios_mas_especificos(
						dicc_ASOrigen_esp_ipv4,dicc_ASOrigen_esp_ipv6,
						tipo_prefijo,AS_origen,prefijo_total,prepending_origen)
				
            numero_elemento = numero_elemento + 1
        
#Etiqueta de nombre para almacenar el fichero
rrc = "_06"        
#Modificacion del diccionario de AS_PATHs para facilitar su manejo posterior
dicc_ASPATHs_final = almacenar_dicc_ASPATHs_final(dicc_ASPATHs)

#Almacenamiento en fichero CSV de informacion de prefijos + vecinos
labels = ["PrefijoCompleto","Vecino","Prepending",'totales','ASprepending','prefijo','longitud',"IPv4","IPv6"]
dataframe_csv_pref_vecinos = pd.DataFrame.from_dict(dicc_pref_vecinos,orient='index',columns = labels)
dataframe_csv_pref_vecinos.to_csv("ResultadosCSV/Prefijos_Vecinos/DiaRCC/Prefijo_Vecino_" + date_start + "-" + date_end + rrc + ".csv",index=False)

#Almacenamiento en fichero CSV de informacion de monitor + prefijos + vecinos
labels = ["ASMonitor","PrefijoCompleto","Vecino","Prepending",'totales','ASprepending','prefijo','longitud',"IPv4","IPv6"]
dataframe_csv_monitor_pref_vecinos = pd.DataFrame.from_dict(dicc_monitor_pref_vecinos,orient='index',columns = labels)
dataframe_csv_monitor_pref_vecinos.to_csv("ResultadosCSV/Prefijos_Vecinos/DiaRCC/Monitor_Prefijo_Vecino_" + date_start + "-" + date_end + rrc +".csv")

#Almacenamiento en fichero CSV de informacion de ASes origen y de transito
labels_origen = ["Monitor","ASOrigen","Prepending","Totales"]
labels_transito = ["Monitor", "ASTransito","Prepending","Totales"]
dataframe_csv_origen = pd.DataFrame.from_dict(diccionario_origen,orient='index',columns = labels_origen)
dataframe_csv_transito = pd.DataFrame.from_dict(diccionario_transito,orient='index',columns = labels_transito)
dataframe_csv_origen.to_csv("ResultadosCSV/ASes/DiaRCC/ASes_origen_" + date_start + "-" + date_end + rrc + ".csv",index=False)
dataframe_csv_transito.to_csv("ResultadosCSV/ASes/DiaRCC/ASes_transito_" + date_start + "-" + date_end + rrc + ".csv",index=False)

#Almacenamiento en fichero CSV de informacion de AS_PATH
labels = ["ASPATH","PrefijosAnunciados","Prepending","Apariciones","Num_ASesPrepending","MayorPrepending","ASesPrepending",
          "DistanciaASesPrepending","IPv4","IPv6","Monitor","LongitudASPATH"]
dataframe_csv_aspath_final = pd.DataFrame.from_dict(dicc_ASPATHs_final,orient='index',columns = labels)
dataframe_csv_aspath_final.to_csv("ResultadosCSV/ASPATH/DiaRCC/ASPATH_" + date_start + "-" + date_end + rrc + ".csv",index=False)

#Almacenamiento en fichero CSV de informacion de longitud de prefijo
labels_long = ["LongitudASPATH","Longitud","Prepending", "Total"]
labels_total = ["Longitud","Prepending", "Total"]
labels_monitores = ["Monitor","Longitud","Prepending", "Total"]

dataframe_csv_longitud_total_ipv4 = pd.DataFrame.from_dict(diccionario_longitudes_total,orient='index',columns = labels_total)
dataframe_csv_longitud_total_ipv6 = pd.DataFrame.from_dict(diccionario_longitudes_total_ipv6,orient='index',columns = labels_total)
dataframe_csv_longitud_monitor = pd.DataFrame.from_dict(diccionario_longitudes_monitores,orient='index',columns = labels_monitores)
dataframe_csv_longitud_total_long_ipv4 = pd.DataFrame.from_dict(diccionario_longitudes_total_long,orient='index',columns = labels_long)
dataframe_csv_longitud_total_long_ipv6 = pd.DataFrame.from_dict(diccionario_longitudes_total_long_ipv6,orient='index',columns = labels_long)

dataframe_csv_longitud_total_ipv4.to_csv("ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv4_" + date_start + "-" + date_end + rrc + ".csv",index=False)
dataframe_csv_longitud_total_ipv6.to_csv("ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv6_" + date_start + "-" + date_end + rrc + ".csv",index=False)
dataframe_csv_longitud_monitor.to_csv("ResultadosCSV/Longitudes/DiaRCC/Longitudes_monitores_" + date_start + "-" + date_end + rrc + ".csv",index=False)
dataframe_csv_longitud_total_long_ipv4.to_csv("ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv4_longaspath_" + date_start + "-" + date_end + rrc  + ".csv",index=False)
dataframe_csv_longitud_total_long_ipv6.to_csv("ResultadosCSV/Longitudes/DiaRCC/Longitudes_total_ipv6_longaspath_" + date_start + "-" + date_end + rrc + ".csv",index=False)

#Almacenamiento en fichero CSV de informacion de prefijos mas especificos

labels1 = ["MascarasIP","DiccionariosIP"]
dataframe_csv_ASOrigen_esp_ipv4 = pd.DataFrame.from_dict(dicc_ASOrigen_esp_ipv4,orient='index',columns = labels1)
dataframe_csv_ASOrigen_esp_ipv6 = pd.DataFrame.from_dict(dicc_ASOrigen_esp_ipv6,orient='index',columns = labels1)

dataframe_csv_ASOrigen_esp_ipv4.to_csv("ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv4_" + date_start  + "-" + date_end + rrc + ".csv")
dataframe_csv_ASOrigen_esp_ipv6.to_csv("ResultadosCSV/Mas_Especificos/DiaRCC/MasEspecificos_ipv6_" + date_start  + "-" + date_end + rrc + ".csv")


elapsed_time = time() - start_time

print("Tiempo de ejecucion: " + str(elapsed_time))
