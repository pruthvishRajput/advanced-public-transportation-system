#!/usr/bin/python
import json
import optparse
import math
from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar
import time

def HandlerForNALocation(inputFile, path, OPpath):
	'''
	input: raw location records
	output: void
	Handles the records corresponding to location unavailability and saves the location record in the new file in OPpath directory'''
	outputFile = inputFile

	Locations=open(path+inputFile,'r')
	LocationsString=Locations.read()

	LocationsJSON=json.loads("["+LocationsString+"]")

	LocationCSV=""
	LocationUnavailableCount = 0
	NewValue = False
	LocationJSONSTring =""

	for Location in LocationsJSON:

		if len ( Location ) == 2:
			LocationUnavailableCount += 1
			NewValue = True 

		if len ( Location ) == 5:
			'''
			s,mod=divmod(float(Location["Time"]),1000)
			dateTimeOP=datetime.fromtimestamp(s).strftime('%d_%m_%Y__%H_%M_%S')
			'''
			LocationJSON = Location
			LocationJSON['Partition'] = LocationUnavailableCount
			LocationJSONSTring = LocationJSONSTring +','+ json.dumps(LocationJSON)
			'''
			LocationCSV=LocationCSV+Location["Time"]+","+Location["Latitude"]+","+Location["Longitude"]+","+Location["Accuracy"]+","+Location["Speed"]+","+str(LocationUnavailableCount)+"\n"
			'''
			LocationUnavailableCount = 0
		elif len ( Location ) == 4:
			'''
			s,mod=divmod(float(Location["Time"]),1000)
			dateTimeOP=datetime.fromtimestamp(s).strftime('%d_%m_%Y__%H_%M_%S')
			'''
			LocationJSON = Location
			LocationJSON['Partition'] = LocationUnavailableCount
			LocationJSONSTring = LocationJSONSTring +','+ json.dumps(LocationJSON)
			'''
			LocationCSV=LocationCSV+Location["Time"]+","+Location["Latitude"]+","+Location["Longitude"]+","+Location["Accuracy"]+","+Location["Speed"]+","+str(LocationUnavailableCount)+"\n"
			'''
			LocationUnavailableCount = 0

		'''If condition ensures the version where LocationUnAvail was not used, doesnt lets to write empty file'''
	LocationCSVFile=open(OPpath+outputFile,'w')
	LocationCSVFile.write(LocationJSONSTring[1:])
		

