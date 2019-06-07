#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Codigo que parsea la informacion comprimida en formato gz a formato txt.
Se realiza por cada colector independientemente.
Se encuentra basado en el proyecto: https://github.com/t2mune/mrtparse
Recomendado por RIPE NCC
'''

"""-----Librerias utilizadas -----"""

import sys, argparse, copy
from datetime import *
from mrtparse import * # PYTHONPATH=/srv/agarcia/TFM-BGP/DATA_Generation/mrtparse python mrtparsebgp.py
from os import listdir,mkdir;

#Colector a parsear
rrc = 'rrc23.ripe'
#Se crea el directorio donde se incluyen las trazas parseadas
mkdir("/srv/agarcia/TFM-BGP/DATA_TXT/"+rrc)

''' Se obtiene el nombre de todos los ficheros comprimidos para un colector'''
list_files = [];

for file in listdir("/srv/agarcia/TFM-BGP/DATA/"+rrc):
    list_files.append(file);

list_files.sort();

peer = None

''' Clase encargada de parsear los ficheros comprimidos a txt'''
class BgpDump:
    __slots__ = [
        'type', 'num', 'ts',
        'org_time', 'flag', 'peer_ip', 'peer_as', 'nlri', 'withdrawn',
        'as_path', 'origin', 'next_hop', 'local_pref', 'med', 'comm',
        'atomic_aggr', 'aggr', 'as4_path', 'as4_aggr', 'old_state', 'new_state',
    ]

    def __init__(self):
        self.type = ''
        self.num = 0
        self.ts = 0
        self.org_time = 0
        self.flag = ''
        self.peer_ip = ''
        self.peer_as = 0
        self.nlri = []
        self.withdrawn = []
        self.as_path = []
        self.origin = ''
        self.next_hop = []
        self.local_pref = 0
        self.med = 0
        self.comm = ''
        self.atomic_aggr = 'NAG'
        self.aggr = ''
        self.as4_path = []
        self.as4_aggr = ''
        self.old_state = 0
        self.new_state = 0

    def print_line(self, prefix, next_hop, file_result):
        d = self.ts
        #d = str(d) Para ver el timestamp sin formato human
        d = datetime.utcfromtimestamp(d).strftime('%m/%d/%y %H:%M:%S')

        if self.flag == 'B' or self.flag == 'A':
            file_result.write('%s|%s|%s|%s|%s|%s|%s|%s|%s|%d|%d|%s|%s|%s|\n' % (
                                self.type, d, self.flag, self.peer_ip, self.peer_as, prefix,
                                self.merge_as_path(), self.origin,next_hop, self.local_pref,
                                self.med, self.comm,self.atomic_aggr, self.merge_aggr()))
        elif self.flag == 'W':
            file_result.write('%s|%s|%s|%s|%s|%s\n' % (
                                self.type, d, self.flag, self.peer_ip, self.peer_as,
                                prefix))
        elif self.flag == 'STATE':
            file_result.write('%s|%s|%s|%s|%s|%d|%d\n' % (
                                self.type, d, self.flag, self.peer_ip, self.peer_as,
                                self.old_state, self.new_state))

    def print_routes(self, file_result):
        for withdrawn in self.withdrawn:
            if self.type == 'BGP4MP':
                self.flag = 'W'
            self.print_line(withdrawn, '',file_result)
        for nlri in self.nlri:
            if self.type == 'BGP4MP':
                self.flag = 'A'
            for next_hop in self.next_hop:
                self.print_line(nlri, next_hop,file_result)

    def td_v2(self, m,file_result):
        global peer
        self.type = 'TABLE_DUMP2'
        self.flag = 'B'
        self.ts = m.ts
        if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
            peer = copy.copy(m.peer.entry)
        elif (m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
            or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
            or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
            or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
            self.num = m.rib.seq
            self.nlri.append('%s/%d' % (m.rib.prefix, m.rib.plen))
            for entry in m.rib.entry:
                self.org_time = entry.org_time
                self.peer_ip = peer[entry.peer_index].ip
                self.peer_as = peer[entry.peer_index].asn
                self.as_path = []
                self.origin = ''
                self.next_hop = []
                self.local_pref = 0
                self.med = 0
                self.comm = ''
                self.atomic_aggr = 'NAG'
                self.aggr = ''
                self.as4_path = []
                self.as4_aggr = ''
                for attr in entry.attr:
                    self.bgp_attr(attr)
                self.print_routes(file_result)

    def bgp4mp(self, m, count,file_result):
        self.type = 'BGP4MP'
        self.ts = m.ts
        self.num = count
        self.org_time = m.ts
        self.peer_ip = m.bgp.peer_ip
        self.peer_as = m.bgp.peer_as
        if (m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            self.flag = 'STATE'
            self.old_state = m.bgp.old_state
            self.new_state = m.bgp.new_state
            self.print_line([], '',file_result)
        elif (m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            if m.bgp.msg.type != BGP_MSG_T['UPDATE']:
                return
            for attr in m.bgp.msg.attr:
                self.bgp_attr(attr)
            for withdrawn in m.bgp.msg.withdrawn:
                self.withdrawn.append(
                    '%s/%d' % (withdrawn.prefix, withdrawn.plen))
            for nlri in m.bgp.msg.nlri:
                self.nlri.append('%s/%d' % (nlri.prefix, nlri.plen))

            self.print_routes(file_result)

    def bgp_attr(self, attr):
        if attr.type == BGP_ATTR_T['ORIGIN']:
            self.origin = ORIGIN_T[attr.origin]
        elif attr.type == BGP_ATTR_T['NEXT_HOP']:
            self.next_hop.append(attr.next_hop)
        elif attr.type == BGP_ATTR_T['AS_PATH']:
            self.as_path = []
            for seg in attr.as_path:
                if seg['type'] == AS_PATH_SEG_T['AS_SET']:
                    self.as_path.append('{%s}' % ','.join(seg['val']))
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as_path.append('(' + seg['val'][0])
                    self.as_path += seg['val'][1:-1]
                    self.as_path.append(seg['val'][-1] + ')')
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as_path.append('[%s]' % ','.join(seg['val']))
                else:
                    self.as_path += seg['val']
        elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            self.med = attr.med
        elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
            self.local_pref = attr.local_pref
        elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
            self.atomic_aggr = 'AG'
        elif attr.type == BGP_ATTR_T['AGGREGATOR']:
            self.aggr = '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
        elif attr.type == BGP_ATTR_T['COMMUNITY']:
            self.comm = ' '.join(attr.comm)
        elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
            self.next_hop = attr.mp_reach['next_hop']
            if self.type != 'BGP4MP':
                return
            for nlri in attr.mp_reach['nlri']:
                self.nlri.append('%s/%d' % (nlri.prefix, nlri.plen))
        elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
            if self.type != 'BGP4MP':
                return
            for withdrawn in attr.mp_unreach['withdrawn']:
                self.withdrawn.append(
                    '%s/%d' % (withdrawn.prefix, withdrawn.plen))
        elif attr.type == BGP_ATTR_T['AS4_PATH']:
            self.as4_path = []
            for seg in attr.as4_path:
                if seg['type'] == AS_PATH_SEG_T['AS_SET']:
                    self.as4_path.append('{%s}' % ','.join(seg['val']))
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as4_path.append('(' + seg['val'][0])
                    self.as4_path += seg['val'][1:-1]
                    self.as4_path.append(seg['val'][-1] + ')')
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as4_path.append('[%s]' % ','.join(seg['val']))
                else:
                    self.as4_path += seg['val']
        elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.as4_aggr = '%s %s' % (attr.as4_aggr['asn'], attr.as4_aggr['id'])

    def merge_as_path(self):
        if len(self.as4_path):
            n = len(self.as_path) - len(self.as4_path)
            return ' '.join(self.as_path[:n] + self.as4_path)
        else:
            return ' '.join(self.as_path)

    def merge_aggr(self):
        if len(self.as4_aggr):
            return self.as4_aggr
        else:
            return self.aggr


'''Funcion principal del programa'''
def main():
	
	# Bucle que recorre todos los ficheros de un colector y realiza el parseo de cada uno
	# haciendo uso de la clase BgpDump
	# Los ficheros comprimidos se encuentran en la url /srv/agarcia/TFM-BGP/DATA/ y 
	# se almacenan parseados en la url /srv/agarcia/TFM-BGP/DATA_TXT/
    for file in range(0,len(list_files)):
	
        name_file = list_files[file];
        d = Reader("/srv/agarcia/TFM-BGP/DATA/"+rrc+"/" + name_file)
        path = str("/srv/agarcia/TFM-BGP/DATA_TXT/"+rrc+"/" + name_file + ".txt");
        file_result = open(path, "w")
		
        count = True;
        for m in d:
            if count:
                m = m.mrt
                if m.err:
                    continue
                b = BgpDump()

                if m.type == MRT_T['TABLE_DUMP_V2']:
                    b.td_v2(m,file_result)
                elif m.type == MRT_T['BGP4MP']:
                    b.bgp4mp(m, count,file_result)
                else:
                    print("Type unknown!")
                    sys.exit();
            else:
                break;

        file_result.close()
        count = False;

if __name__ == '__main__':
    main()
# Las trazas parseadas de la ruta /srv/agarcia/TFM-BGP/DATA/ se almacenan en /srv/agarcia/TFM-BGP/DATA_TXT/
# Con la variable rrc = 'rrc23.ripe' se indica el colector a parsear
