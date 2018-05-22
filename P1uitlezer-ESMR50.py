#!/usr/bin/python
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# DSMR P1 uitlezer
# (c) 11-2017 2016 - GJ - gratis te kopieren en te plakken

versie = "1.2"
import sys
import serial
import time

################
#Error display #
################
def show_error():
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout type: %s" % ft )
    print("Fout waarde: %s" % fv )
    return

################################################################################################################################################
#Main program
################################################################################################################################################
#print ("DSMR 5.0 P1 uitlezer",  versie)
#print ("Control-C om te stoppen")

#Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize=serial.EIGHTBITS
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port="/dev/ttyUSB0"

def get_dsmr_data (lines):
	" open ser, read lines, close ser "

	#Open COM port
	try:
	    ser.open()
	except:
	    print "Fout bij het openen van %s. Programma afgebroken."  % ser.name
	    return 

	#DSMR Model:
	model = "2M550E-1011"
	modelcount = 0

	while modelcount < 2:
	    p1_line=''
	#Read 1 line
	    try:
		p1_raw = ser.readline()
	    except:
		print "error reading line from ser"
		return

	    p1_str=str(p1_raw)
	    if model in p1_str:
		modelcount = modelcount + 1

	    #p1_str=str(p1_raw, "utf-8")
	    p1_line=p1_str.strip('\0\r\n')
	    if modelcount == 1:
		lines.append(p1_line)

	    
	#Close port and show status
	try:
	    ser.close()
	except:
	    print "problem with serial port"
	    return
### end function

lines=[]
count=0
while  len(lines) < 10:
	get_dsmr_data(lines);
	close_line_found=0
	for l in lines:
		if '!' in l:
			close_line_found=1
	
	if close_line_found == 0:
		lines=[]
		time.sleep(2)
	count=count+1
	if count > 4:
		print "failed to read serial port correctly"
		sys.exit(1)

#for l in lines:
#	print l
print('\n'.join(map(str, lines)))




