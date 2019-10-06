#!/usr/bin/python
import json
import optparse
from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar
import time
from pymongo import     MongoClient
from operator import itemgetter, attrgetter
import os
import pytz

con = MongoClient()

def add_dt(places_copy,RecordType):
	'''
	input: raw location records
	output: raw location records with 'dt' element added into it
	function: adds the epoch time JSON element into location record JSON if time is not in epoch else returns the epoch time in 'dt' filed
	'''
	for place in places_copy:
		if RecordType == 'RawRecord':
			place['epoch']=1000*time.mktime(time.strptime(place['Time'],'%d %b %Y %H:%M:%S'))
		else:
			place['epoch'] = place ['Time']
        
	return(places_copy)

#inputFile = options.inputFile

def ReadLocationRecordsAndSeparateIntoSegement(RouteName, inputFile, path, RecordType):
	'''
	input: raw location records
	output: void
	function: 
	1. Separates the raw location records into different trip records, if the time between two consecutive records is greater than 30 min. and saves it into MongoDB. 
	2. A status information related to the given trip is maintained after every operation in 'TripInfo' Collection. This is further used at every stages to extract relevant record at each stage of execution.'''

	print('Reading file: '+inputFile)

	'''Separate the trip information'''
	LocationTripTagList = inputFile.split('?')
	LocationTripTag = LocationTripTagList[0] 

	'''initialize the MongoClient connection'''
	con = MongoClient()
	#path = '/home/pruthvish/JRF/LocationsRead/ISCON_PDPU_Reords/RawRecord/'
	Locations=open(path+'/'+inputFile,'r')
	LocationsString=Locations.read()
	LocationsJSONRecord=json.loads("["+LocationsString+"]")


	'''For unique location record'''
	LocationsJSONUnSorted = list({ each ['Time'] : each for each in LocationsJSONRecord }.values())


	''' For TripRecorder version -0 '''
	LocationsJSONUnSorted=add_dt(LocationsJSONUnSorted,RecordType)


	'''LocationsJSON is in random seq. Hence it needs to be sorted before applying separate logic'''
	LocationsJSON = sorted(LocationsJSONUnSorted, key=itemgetter('epoch'))


	s,mod=divmod(float(LocationsJSON[0]["epoch"]),1000)

	# get time in tz
	tz = pytz.timezone('Asia/Kolkata')
	#tz = pytz.timezone('Asia/Calcutta')
	dateTimeOP=datetime.fromtimestamp(s,tz).strftime('%d_%m_%Y__%H_%M_%S')

	'''Register Route and trip info in RouteInfo DB'''
	RouteInfo = 'RouteInfo'
	RouteList = LocationTripTag.split('+')
	Route = RouteList [0]
	TripID = RouteList [1]
	#query = con[RouteInfo][RouteInfo].find({'id':Route}).limit(1)
	query = con[RouteInfo][RouteInfo].update_one({'RouteTag':Route},{'$addToSet':{'TripID':TripID}},True)


	'''Register MongoCollection in TripInfo collection'''
	TripInfo = 'TripInfo'
	MongoCollection = dateTimeOP
	#con[LocationTripTag][TripInfo].insert_one({'SingleTripInfo':MongoCollection,'filteredLocationRecord':False,'DBSCANOp':False,'segments':-1,'segmentsTimeStamp':[]})
	con[RouteName][TripInfo].insert_one({'SingleTripInfo':MongoCollection,'filteredLocationRecord':False,'DBSCANOp':False,'segments':-1,'segmentsTimeStamp':[]})
	LocationCount=len(LocationsJSON)


	for index in range(0,LocationCount):
		'''Separate the trip if the time between two consecutive records is greater than 30 min'''
		if ((index>0) and (float(LocationsJSON[index]["epoch"])-float(LocationsJSON[index-1]["epoch"])>(30*60*1000))):
			
			s,mod=divmod(float(LocationsJSON[index]["epoch"]),1000)
			# get time in tz
			tz = pytz.timezone('Asia/Kolkata')
			#tz = pytz.timezone('Asia/Calcutta')
			dateTimeOP=datetime.fromtimestamp(s,tz).strftime('%d_%m_%Y__%H_%M_%S')

			MongoCollection = dateTimeOP
			'''Register MongoCollection in TripInfo collection'''
			#con[LocationTripTag][TripInfo].insert_one({'SingleTripInfo':MongoCollection,'filteredLocationRecord':False,'DBSCANOp':False,'segments':-1,'segmentsTimeStamp':[]})		
			con[RouteName][TripInfo].insert_one({'SingleTripInfo':MongoCollection,'filteredLocationRecord':False,'DBSCANOp':False,'segments':-1,'segmentsTimeStamp':[]})
		#input()
		LocationRecord = {}
		LocationRecord['epoch'] = float(LocationsJSON[index]["epoch"])
		LocationRecord['Longitude'] = float (LocationsJSON[index]["Longitude"])
		LocationRecord['Latitude'] = float (LocationsJSON[index]["Latitude"])
		LocationRecord['Accuracy'] = float (LocationsJSON[index]["Accuracy"])
				
		if RecordType == 'RawRecordEpochSpeed':
			LocationRecord['Speed'] = LocationsJSON[index]["Speed"]
		
		#con[LocationTripTag][MongoCollection+".LocationRecords"].insert_one(LocationRecord)
		#con[LocationTripTag][MongoCollection+".RawRecords"].insert_one(LocationRecord)

		con[RouteName][MongoCollection+".RawRecords"].insert_one(LocationRecord)

def HandlerForNALocation(inputFile, path, OPpath):
	'''
	input: raw location records
	output: void
	Handles the records corresponding to location unavailability and saves the location record in the new file in OPpath directory'''

	outputFile = inputFile

	Locations=open(path+'/'+inputFile,'r')
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
	LocationCSVFile=open(OPpath+'/'+outputFile,'w')
	LocationCSVFile.write(LocationJSONSTring[1:])

	
		

