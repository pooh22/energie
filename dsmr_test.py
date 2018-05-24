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
    'feedin':'1-0:2.7.0',
    'allpf':'0-0:96.7.21',
    'longpf':'0-0:96.7.9',
    '0-0:1.0.0':'timestamp',
    '1-0:1.8.1':'meter1',
    '1-0:1.8.2':'meter2',
    '1-0:2.8.1':'feedin1',
    '1-0:2.8.2':'feedin2',
    '0-0:96.14.0':'tariff',
    '1-0:1.7.0':'using',
    '1-0:2.7.0':'feedin',
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
    d['sma.spots'] = ""
    unitof = {}
    for line in lines:
        linefmt = re.search( r'(Device.Status|Device.Temperature|EToday|ETotal|Pdc):', line, re.I )
        if linefmt:
            if "Device Status" in line:
                matchobj = re.match ( r'Device.Status: (.*)$', line)
                if matchobj:
                    d['sma.device.status'] = matchobj.group(1)
                else:
                    print "problem matching device status line"
            elif "Device Temperature" in line:
                #matchobj = re.match ( r'Device.Temperature: (\d\.\d+)(..)$', line)
                matchobj = re.match ( r'Device.Temperature: (.*)(...)', line)
                if matchobj:
                    d['sma.device.temperature'] = matchobj.group(1)
                    unitof['sma.device.temperature'] = "C"
                else:
                    print "problem matching device temperature line"
            elif "EToday" in line:
                matchobj = re.match ( r'.*EToday: (\d+\.\d+)', line)
                if matchobj:
                    d['sma.prod.etoday'] = matchobj.group(1)
                    unitof['sma.prod.etoday'] = "kWh"
                else:
                    print "problem matching prod etoday line"
            elif "ETotal" in line:
                matchobj = re.match ( r'.*ETotal: (\d+\.\d+)', line)
                if matchobj:
                    d['sma.prod.etotal'] = matchobj.group(1)
                    unitof['sma.prod.etotal'] = "kWh"
                else:
                    print "problem matching prod etotal line"
            elif "Pdc" in line:
                matchobj = re.match ( r'\s+(.*?) Pdc: +(\d+\.\d+)kW.*?Udc: +(\d+\.\d+)V.*?Idc: +(\d+\.\d+)A', line)
                if matchobj:
                    safename = matchobj.group(1)
                    safename = re.sub(r'\s', '_', safename)
                    safename = 'sma.spot.' + safename
                    d['sma.spots'] = d['sma.spots'] + " " + safename
                    d[safename + '.pdc'] = matchobj.group(2)
                    unitof[safename + '.pdc'] = "kW"
                    d[safename + '.udc'] = matchobj.group(3)
                    unitof[safename + '.udc'] = "V"
                    d[safename + '.idc'] = matchobj.group(4)
                    unitof[safename + '.idc'] = "A"
                else:
                    print "problem matching prod etotal line"
           
    for k in unitof:
        kunit = k + "-unit"
        d[kunit] = unitof[k]
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
# or....
# use local system time for both

    return d

	
if __name__ == '__main__':
    sma_rawdata = netcat( sma_host, sma_port)
    sma_data = sma_fill( sma_rawdata)
#    for k in sma_data:
#        print "sma", k, sma_data[k]

    dsmr_rawdata = netcat( dsmr_host, dsmr_port)
    dsmr_data = dsmr_fill( dsmr_rawdata)
#    for k in dsmr_data:
#        print "dsmr", k, " = ", dsmr_data[k]
    if not 'using' in dsmr_data:
        dsmr_data['using'] = 0

    prod_tot = 0.0 # kW
    for spot in sma_data['sma.spots'].split():
        prod_tot = prod_tot + float(sma_data[ spot + '.pdc'])

    message = "prod=" + '%.3f' % prod_tot + "kW use=" + '%.3f' % float(dsmr_data['using']) + 'kW feedin=' + '%.3f' % float(dsmr_data['feedin']) + 'kW' 
    perfdata = "|prod=" + '%.3f' % prod_tot + " use=" + '%.3f' % float(dsmr_data['using']) + ' feedin=' + '%.3f' % float(dsmr_data['feedin']) 
    perfdata = perfdata + ' realuse=' '%.3f' % (float(dsmr_data['using']) +( prod_tot -  float(dsmr_data['feedin'])) )

    print message + perfdata
