#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programa que descarga toda las trazas de RIPE NCC de todos los colectores para
una determinada fecha (por defecto para el 10 de enero de 2018)
@author: kevin
"""

"""-----Librerias utilizadas -----"""
from urllib.request import urlopen
from os import listdir,mkdir;
import re
import wget

'''-------    FUNCIONES     -------'''

'''obtener_ficheros_dia:
		Funcion que tiene como argumentos un colector y una fecha (en formato de anos.meses)
		Y devuelve una lista con todos los ficheros disponibles para el dia indicado en el interior
		de la función y que coinciden con los argumentos.
		
'''
def obtener_ficheros_dia(rrc,date):
	
	#Se comprueba que los ficheros se encuentran disponibles, si no lo estan se devuelve un -1
    try:
	
		#Direccion web donde se encuentran las trazas
        url = 'http://data.ris.ripe.net/' + rrc + '/' + date;
		#Obtener los ficheros que coinciden con el formato "bview.20180110.*.gz" o "updates.20180110.*.gz"
        website = urlopen(url)
        html = website.read()
        html = html.decode("utf-8")
        files = re.findall('href="(bview.20180110.*.gz)"', html)
        files2 = re.findall('href="(updates.20180110.*.gz)"', html)
        files.reverse()
        files2.reverse()
        files.extend(files2)

    except:
	
        files = -1
		
    return [files,url]

	
'''-------    main     -------'''

#Fecha de las trazas (Ano.Mes)
date = '2018.01'

#Bucle para realizar la funcion para todos los colectores disponibles (hasta el 24)
for rrc_num in range(0,24):

	# Se descarta el colector 22 al tener un formato de trazas inadecuado
    if rrc_num != 22:
		
		#Debido al formato de colectores. Por ejemplo el colector 2 tiene de nombre rrc02,
		#se debe anadir el 0 en caso de que sea un numero de colector menor al 10.
        if rrc_num < 10:

            rrc = 'rrc0' + str(rrc_num)

        else:

            rrc = 'rrc'+str(rrc_num)

        source = rrc+'.ripe'
		#Se obtiene todos los ficheros  para el colector y dia indicado
        [files,url] = obtener_ficheros_dia(rrc,date)
		#Si no ha habido errores para obtener los ficheros se descargan en un directorio
        if files != -1:

            mkdir("/srv/agarcia/TFM-BGP/DATA/" + source);
            output_directory = "/srv/agarcia/TFM-BGP/DATA/" + source;

            for file_sub in files:
			
                filename = wget.download(url + "/" + file_sub, out=output_directory)

print ('Download Completed!');
# Se descarga todas las trazas en /srv/agarcia/TFM-BGP/DATA/ 