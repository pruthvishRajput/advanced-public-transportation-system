#!/usr/bin/python
import optparse
from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar
import time
import json
import numpy
import math
from pymongo import     MongoClient

con = MongoClient()

def mydistance(a1,b1,a2,b2):
	'''
	input: location attributes corresponding to point 1 and 2. (lat1, lon1, lat2, lon2)
	output: distance between point 1 and point 2
	function: compute distance between two points using haversine formula
	'''
	R=6371e3
	x1=math.radians(a1)
	y1=math.radians(b1)
	x2=math.radians(a2)
	y2=math.radians(b2)
	delx=x2-x1
	dely=y2-y1
	c=math.sin(delx/2)*math.sin(delx/2)+math.cos(x1)*math.cos(x2)*math.sin(dely/2)*math.sin(dely/2)
	d=2*math.atan2(math.sqrt(c),math.sqrt(1-c))
	e=R*d
	return(e)

def addRecords(locationsCopy, indexCopy,diff, RouteName,SingleTripInfo):
	'''
	input: location records, index for identifying the location records between which interpolation needs to be performed, diff for duration of GPS outage and the information related to database (RouteName) and trip for which interpolation procedure will be executed
	output: void
	function: Apply interpolation add records between the two points The resultant records are stored into MongoDB collection.
	'''
	Longitude1Float = locationsCopy[indexCopy]['Longitude']
	Latitude1Float = locationsCopy[indexCopy]['Latitude']
	Longitude2Float = locationsCopy[indexCopy+1]['Longitude']
	Latitude2Float = locationsCopy[indexCopy+1]['Latitude']

	AccuracyAvg=(locationsCopy[indexCopy+1]['Accuracy']+locationsCopy[indexCopy]['Accuracy'])/2
	stepLat=(Latitude2Float-Latitude1Float)/diff
	stepLon=(Longitude2Float-Longitude1Float)/diff
    
	initialEpoch=locationsCopy[indexCopy]['epoch']

	Epoch=initialEpoch
	Lat=Latitude1Float
	Lon=Longitude1Float
	insertIndex=indexCopy
	for index in range(1,diff):
		#Epoch=Epoch+1000
		#Lat=Lat+stepLat
		#Lon=Lon+stepLon
		#insertIndex=insertIndex+1
        
		location={}
		location["epoch"]=Epoch+index*1000
		location["Latitude"]=Lat+index*stepLat
		location["Longitude"]=Lon+index*stepLon
		location["Accuracy"]=AccuracyAvg
		#location["Tag"]="New"

		con[RouteName] [SingleTripInfo+'.Filtered'].insert_one(location)

def ApplyFiltering(RouteName,SingleTripInfo):
	'''
	input: The information related to database (RouteName) and trip for which filtering procedure will be executed.
	output: void
	function: Apply filtering procedure (outlier removal, segmentation and interpolation), and store the filtered record into MongoDB collection with '.Filtered' collection hierarchy.
	'''

	'''Save the collection copy for filtering'''
	print('Executing filtering on ' + SingleTripInfo)
	LocationsJSONList = [LocationRecord for LocationRecord in con [RouteName] [SingleTripInfo+'.RawRecords'].find().sort([('epoch',1)])]

	for indexk in range(len(LocationsJSONList)):
	    del LocationsJSONList[indexk]['_id']

	con[RouteName][SingleTripInfo+'.Filtered'].insert_many(LocationsJSONList)


	'''outlier removal based on the accuracy'''
	Accuracy = []
	for lr in LocationsJSONList:
		Accuracy.append(lr['Accuracy'])
	Accuracy=numpy.asarray(Accuracy)
	meanAccuracy=numpy.mean(Accuracy)
	stdAccuracy=numpy.std(Accuracy)
	outlierThresholdAccuracy=meanAccuracy + 2*stdAccuracy

	AccuracyMeasure={}
	AccuracyMeasure['Mean'] = meanAccuracy
	AccuracyMeasure['Std. deviation'] = stdAccuracy

	if outlierThresholdAccuracy != meanAccuracy:
		'''Remove outlier from the collection'''
		con[RouteName] [SingleTripInfo+'.Filtered'].delete_many({ 'Accuracy':{'$gte':  outlierThresholdAccuracy}  })
	#uniqueStuffWithoutOutliers = [lr for lr in uniqueStuff if float(lr['Accuracy']) <  outlierThresholdAccuracy] 


	'''Segmentation and Interpolation '''

	'''Read LocationRecords and store it in LocationsJSONList'''
	LocationRecords = con [RouteName] [SingleTripInfo+'.Filtered'].find().sort([('epoch',1)])
	LocationsJSONList = [LocationRecord for LocationRecord in LocationRecords]
	TripStartTimeEpoch = LocationsJSONList [0] ['epoch']
	(TripStartTimeEpoch, ms) = divmod (TripStartTimeEpoch,1000)
	TripStartTime = datetime.fromtimestamp(TripStartTimeEpoch).strftime('%H')

	Segments = 1
	LocationsCount=len(LocationsJSONList)
	timeDiff=0
	SegmentsTimeStamps=[]

	'''Segment of First time stamp'''
	SegmentsTimeStamps.append( [ LocationsJSONList[0]['epoch'] ] )
	for index in range(0,LocationsCount-1):
		timeDiff, remainder=divmod(LocationsJSONList[index+1]['epoch']-LocationsJSONList[index]['epoch'],1000)	
		if timeDiff >15:
			distance = mydistance(LocationsJSONList[index+1]['Latitude'],LocationsJSONList[index+1]['Longitude'],LocationsJSONList[index]['Latitude'],LocationsJSONList[index]['Longitude'])

			if distance<60: 
				'''
				Indicates stoppage. Add Location records using interpolation
				'''
				addRecords(LocationsJSONList,index,int(timeDiff),RouteName,SingleTripInfo)	
						
			else:
				'''
				Segment Found
				'''
				SegmentsTimeStamps[Segments-1].append(LocationsJSONList[index]['epoch'])
				SegmentsTimeStamps.append( [ LocationsJSONList[index+1]['epoch'] ] )
				Segments+=1
		elif timeDiff >1:
			addRecords(LocationsJSONList,index,int(timeDiff),RouteName,SingleTripInfo)			

	SegmentsTimeStamps[Segments-1].append(LocationsJSONList[LocationsCount-1]['epoch'])

	'''Relative Std. Dev of accuracy for Auto-Removal of trip'''
	LocationRecords = con [RouteName] [SingleTripInfo+'.Filtered'].find().sort([('epoch',1)])
	LocationsJSONList = [LocationRecord for LocationRecord in LocationRecords]

	Accuracy = []
	for lr in LocationsJSONList:
		Accuracy.append(lr['Accuracy'])
	Accuracy=numpy.asarray(Accuracy)
	meanAccuracy=numpy.mean(Accuracy)
	stdAccuracy=numpy.std(Accuracy)

	RelativeSTDAccuracy = (stdAccuracy/meanAccuracy)*100

	con[RouteName]['TripInfo'].update_one({'SingleTripInfo':SingleTripInfo},{'$set':{'segments':Segments, 'filteredLocationRecord':True, 'segmentsTimeStamp':SegmentsTimeStamps,'meanAccuracy':meanAccuracy,'stdAccuracy':stdAccuracy,'RelativeSTDAccuracy':RelativeSTDAccuracy,'TripStartHour': TripStartTime}})
