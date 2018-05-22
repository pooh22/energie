#!/usr/bin/python
# vim: bg=dark tabstop=4 expandtab shiftwidth=4 softtabstop=4 smarttab smartindent

import socket
import re
import pprint
import string

pp = pprint.PrettyPrinter(indent=4)

sma_host = '192.168.9.57'
sma_port = 7776
dsmr_host = '192.168.9.28'
dsmr_port = 7777

DSMRMAP = { 
    'timestamp':'0-0:1.0.0',
    'meter1':'1-0:1.8.1',
    'meter2':'1-0:1.8.2',
    'feedin1':'1-0:2.8.1',
    'feedin2':'1-0:2.8.2',
    'tariff':'0-0:96.14.0',
    'using':'1-0:1.7.0',
    'feeding':'1-0:2.7.0',
    'allpf':'0-0:96.7.21',
    'longpf':'0-0:96.7.9',
    '0-0:1.0.0':'timestamp',
    '1-0:1.8.1':'meter1',
    '1-0:1.8.2':'meter2',
    '1-0:2.8.1':'feedin1',
    '1-0:2.8.2':'feedin2',
    '0-0:96.14.0':'tariff',
    '1-0:1.7.0':'using',
    '1-0:2.7.0':'feeding',
    '0-0:96.7.21':'allpf',
    '0-0:96.7.9':'longpf',
}

def netcat(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(( host, port ))

    rec_data = []
    while 1:
        data = s.recv(10240)
        if not data:
            break
        rec_data.append(data)

    s.close()
    x = string.join(rec_data, '')
    y = x.split('\n')
        
    return y


def sma_fill(lines):
    "return dictionary with data from lines"
    d = {}
    unitof = {}
    for line in lines:
        linefmt = re.search( r'(Device.Status|Device.Temperature|EToday|ETotal|Pdc):', line, re.I )
        if linefmt:
            print line 
    return d        
    

def dsmr_fill(lines):
    "return dictionary with data from lines"
    d = {}
    unitof = {}
    for line in lines:
        linefmt = re.search( r'^([01]-[01]:[0-9.]+)\((.*?)\)(.*)$', line, re.I|re.M )
        if linefmt:
            k = linefmt.group(1)
            v = linefmt.group(2)
            x = re.search( r'\*(.*)$', v )
            if x :
                unit = x.group(1)
                v = re.sub( r'\*(.*)$', "", v)
                unitof[k] = unit
            d[k] = v

    for k, v in d.items():
        if k in unitof:
            tmpkey = k + "-unit"
            d[ tmpkey ] = unitof[k] # also set the human readable value

        if k in DSMRMAP:
            d[ DSMRMAP[k] ] = d[k] # also set the human readable value
            if k in unitof:
                tmpkey = DSMRMAP[k] + "-unit" 
                d[ tmpkey ] = unitof[k] # also set the human readable value
           
#    if 'timestamp' in d:
## 180522205622S
#        ts = re.search ( r'(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', d['timestamp'] )
#        year = "20" + ts.group(1)
#        month = ts.group(2)
#        day = ts.group(3)
#        hour = ts.group(4)
#        minute = ts.group(5)
#        seconds = ts.group(6)
#        print "timestamp = ", year, month, day, hour, minute, seconds

    return d

	
if __name__ == '__main__':
    sma_rawdata = netcat( sma_host, sma_port)
    sma_data = sma_fill( sma_rawdata)
    for k in sma_data:
        print "sma", k, sma_data[k]

#    dsmr_rawdata = netcat( dsmr_host, dsmr_port)
#    dsmr_data = dsmr_fill( dsmr_rawdata)
#    for k in dsmr_data:
#        print k, " = ", dsmr_data[k]
