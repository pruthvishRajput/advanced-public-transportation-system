#!/usr/bin/python
# coding: utf-8

# In[13]:


#|||Indexing of bus stand|||

import time as t
from sklearn.cluster import DBSCAN

from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar

import json
import numpy
import math
#import geocoder

from pymongo import MongoClient
import optparse
import folium

# In[14]:


def mydistance(origin, destination):
	'''
	input: location attributes corresponding to point 1 and 2. (lat1, lon1, lat2, lon2)
	output: distance between point 1 and point 2
	function: compute distance between two points using haversine formula
	'''
	lat1, lon1 = origin
	lat2, lon2 = destination
	radius = 6371000 # meters

	dlat = math.radians(lat2-lat1)
	dlon = math.radians(lon2-lon1)
	a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))         * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = radius * c

	#return squared distance 
	return d

def InitializeMap(LocationRecord):
	'''
	input: 
	output: 
	function: 
	'''
	'''OSM Map initialization'''
	map_osm = folium.Map(location=[float(LocationRecord[0]['Latitude']),float(LocationRecord[0]['Longitude'])],zoom_start=11)
	PolyPoints=[]
	for index in range(0,len(LocationRecord)):
		if(index*50<len(LocationRecord)-1):
		    PolyPoints.append(tuple([float(LocationRecord[index*50]['Latitude']),float(LocationRecord[index*50]["Longitude"])]))
		#print(type(Y[index][0]))
		#input()
	folium.PolyLine(PolyPoints, color="red", weight=3, opacity=1).add_to(map_osm)
	
	return(map_osm)

def MarkDetectedBusStopOnAMap(LocationTupleList, model, clusters,LocationRecord, map_osm):
	'''
	input: 
	output: 
	function: 
	'''
	'''BusStop Clusters list of list''' 
	BusStop=[]
	GotBusStopTime = []
	BusStopTime = []
	BusStopLocationRecords = []
	
	LocationTupleNumpy = numpy.asarray(LocationTupleList)
	'''List of list (Bus stops)'''
	for BusStopCluster in range(0,clusters):
		BusStop.append([])
		BusStopLocationRecords.append([])
		GotBusStopTime.append(False)

	BusStopCluster = 0
	BusStopClusterPointIndexInNumpy = 0

	for BusStopCluster in model.labels_:
		if BusStopCluster!=-1:
		    
		    BusStop[BusStopCluster].append( LocationTupleNumpy [BusStopClusterPointIndexInNumpy])
		    BusStopLocationRecords[BusStopCluster].append( LocationRecord [BusStopClusterPointIndexInNumpy])
		    if GotBusStopTime [BusStopCluster]== False:
		        BusStopTime.append(LocationRecord[BusStopClusterPointIndexInNumpy]['epoch'])
		        GotBusStopTime[BusStopCluster] = True
		    '''List of List. And List will maintain its order'''
		    
		BusStopClusterPointIndexInNumpy=BusStopClusterPointIndexInNumpy+1

	''' Extract mean of all cluster and associated time stamp of any point belonging to cluster'''
	#SingleTripBusStopInfo = SingleTripInfo + '.BusStopInfo'
	for index in range(0 , clusters):
		busStopLat=numpy.mean([float(x[0]) for x in BusStop[index]])
		busStopLon=numpy.mean([float(x[1]) for x in BusStop[index]])

		folium.Marker([busStopLat,busStopLon], popup=str(index)).add_to(map_osm)

	return(map_osm)

def MarkActualBusStopOnAMap(StoppageList, map_osm, AcutualBusStops, AcutualCrossRoad):
	'''
	input: 
	output: 
	function: 
	'''
	for Stoppage in StoppageList:
		if Stoppage['Type'] == 'BusStop' and AcutualBusStops == True:
			folium.Marker([Stoppage['Location'][0], Stoppage['Location'][1]], popup=Stoppage['Name'], icon=folium.Icon(color='green')).add_to(map_osm)
		elif Stoppage['Type'] == 'CrossRoad' and AcutualCrossRoad == True: 
			folium.Marker([Stoppage['Location'][0], Stoppage['Location'][1]], popup=Stoppage['Name'], icon=folium.Icon(color='red')).add_to(map_osm)
	return(map_osm)
con = MongoClient()



