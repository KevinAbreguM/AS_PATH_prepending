INSTRUCCIONES DE UTILIZACIÓN DEL CÓDIGO.

El proyecto se divide en distintas fases, debido a los largos tiempos de procesamiento, para agilizar las pruebas y obtener
resultados intermedios. Aún así, el tiempo de procesamiento completo es bastante superior a una semana (aunque puede variar dependiendo de la memoria RAM disponible)

Se puede utilizar tanto Python 2 como Python 3, aunque se recomienda utilizar Python 3 al menos en la fase de representación
de resultados.

Se recomienda mantener un formato de carpetas similar, o modificar el código para establecer el formato de carpetas deseado

El orden de las carpetas empleado es:

TFM-BGP

 1.Kevin
 
    - *.py
    - ResultadosCSV   
    - Prefijos 
    - Prefijos_imagenes   
    - ASes
    - ASes_imagenes
    - Longitudes
    - Longitudes_imagenes
    - Mas_Especificos
    - Mas_Especificos_imagenes
    - ASPATH
    - ASPATH_imagenes
    - Prefijos_Vecinos
    - Prefijos_Vecinos_imagenes


*Todas las carpetas dentro de resultadosCSV deben contener una carpeta denominada DiaRCC

*Dentro de la carpeta Kevin se incluyen todo el codigo (todos los ficheros .py) al mismo nivel.

*El formato de carpetas se puede modificar cambiando las rutas incluidas.


El orden de ejecución del código es:

Como pasos iniciales:
  1. Descarga_Trazas
  2. mrtparsebgp_rrcs (se debe instalar la libreria mrtparse)
  3. create_mega_df
  
Para obtener la informacion de cada nivel:
  1. obtencion_info_general (Actualmente se debe ejecutar una vez por cada colector, por lo que se recomienda ejecutar 
  tantas veces como colectores haya disponibles)
  2. obtencion_informacion_prefijos (Actualmente se debe ejecutar una vez por cada colector, por lo que se recomienda ejecutar 
  tantas veces como colectores haya disponibles) 
  
Pasos Intermedios entre obtencion de informacion de cada nivel y representaciones. (Se recomienda que se ejecuta despues de haber realizado
obtencion_info_general para todos los colectores)
  1. Agrupacion_Prefijos_Mas_Especificos
  2. Agrupacion_Prefijos_Mas_Especificos_long24 (OPCIONAL)
  3. obtencion_info_ASes_global (OPCIONAL)
  
Representaciones (Se recomienda utilizar python 3):

  A Nivel prefijos por monitor y obtencion de la distribución por tipo de monitor (proveedores o peers/clientes)
  
    1. Analisis_prefijos
    
  A nivel de ASes origen
  
    1. Procesado_ASes_Origen
    
  A nivel de ASes transito
  
    1. Procesado_ASes_Transito
  
  A nivel de AS_PATH
  
    1. Procesado_ASPATH
    2. Procesado_ASPATH_colector (opcional)
   
  A nivel de longitudes de prefijos
  
    1. Procesado_Longitudes_Prefijo
    2. Procesado_Prepending_PrefijosBase_Longitud24 (opcional) (Unicamente si se ha ejecutado previamente
      Agrupacion_Prefijos_Mas_Especificos_long24)
  
  A nivel de prefijos mas especificos
  
    1. Procesado_Prefijos_Mas_Especificos
  
  A nivel de pares prefijos + AS vecino
  
    1. Procesado_Prefijos_Vecinos
    2. Procesado_Prefijos_Vecinos_Colector (opcional)
  
  
