import json
from pymongo import MongoClient
import math

from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar
import time
import pprint

con = MongoClient()

def InitializeVariableDict():
    VariableDict = {}
    VariableDict['distance'] = []
    VariableDict['distance_index'] = 0
    VariableDict['Bound'] = ''
    VariableDict['BusStopIndex'] = -1
    VariableDict['minDist'] = -1
    VariableDict['arrivedAt'] = -1
    VariableDict['arrivingAt'] = -1
    VariableDict['t_j_p1_1'] = -1
    VariableDict['t_j_p1_2'] = -1
    VariableDict['t_j_p1_predicted'] = -1
    VariableDict['t_j_p1_predictedL'] = -1
    VariableDict['t_j_p1_predictedH'] = -1
    VariableDict['t_j_m1'] = -1
    VariableDict['j_m1'] = -1
    VariableDict['Delta_pt'] = -1
    VariableDict['Delta_ps'] = -1
    VariableDict['t_j_m1_s_predicted'] = -1
    VariableDict['t_j_m1_s_predictedL'] = -1
    VariableDict['t_j_m1_s_predictedH'] = -1
    VariableDict['j_p1_s'] = -1
    VariableDict['t_j_p1_s'] = -1
    VariableDict['t_j_p1_predictedMargin'] = -1
    VariableDict['t_j_m1_s_predictedMargin'] = -1

    '''For sub bus-stops'''
    VariableDict['PredictionTupleList'] = []
    VariableDict['PredictionMarginTupleList'] = []    

    return(VariableDict)


def GetBoundAndHData(LocationRecord,BusStopsList,VariableDict,RouteName):
    BusStopsCount = len(BusStopsList)
    DistFirstStop = mydistance(LocationRecord['Latitude'],LocationRecord['Longitude'],BusStopsList[0]['Location'][0],BusStopsList[0]['Location'][1])
    DistLastStop = mydistance(LocationRecord['Latitude'],LocationRecord['Longitude'],BusStopsList[BusStopsCount-1]['Location'][0],BusStopsList[BusStopsCount-1]['Location'][1])

    TripStartTimeEpoch = LocationRecord ['epoch']
    (TripStartTimeEpoch, ms) = divmod (TripStartTimeEpoch,1000)
    TripStartTime = datetime.fromtimestamp(TripStartTimeEpoch).strftime('%H')

    '''Convert TripStartTime to Int and to str again, to get in line with the one store in SingleTripInfo'''
    #print (TripStartTime)

    if(DistFirstStop < DistLastStop):
        VariableDict['Bound'] = 'North'
        #print('North')

    else:
        VariableDict['Bound'] = 'South'
        #print('South')
        #New Addition for Dist_th
        #BusStopsList = BusStopsListSouth

    

    '''Find Historical TimeDiff for given TripStartTime and given bound'''
    HistoricalDataList = [Record for Record in con[RouteName]['H.'+TripStartTime+'.'+VariableDict['Bound']].find().sort([('id',1)])]
    #print(HistoricalDataList,'H.'+TripStartTime+'.'+VariableDict['Bound'])

    #pprint.pprint(HistoricalDataList)
    return(VariableDict, HistoricalDataList)
    #input()
    '''Along with Bound First stop in the given bound should be taken as arrivedAt and subsequent as arrivingAt'''




'''Indicates arrivedAt: BusStopIndex'''
def GetArrivalStatusNorthBound(LocationRecord,BusStopsList,VariableDict,RouteName,Dist_TH):
    
    BusStopsCount = len (BusStopsList)
    for j in range(0,3):
        if (VariableDict['BusStopIndex']+j) < BusStopsCount:
            DistanceFromStop = mydistance(LocationRecord['Latitude'],LocationRecord['Longitude'],BusStopsList[VariableDict['BusStopIndex']+j]['Location'][0],BusStopsList[VariableDict['BusStopIndex']+j]['Location'][1])
            if DistanceFromStop < Dist_TH:
                VariableDict['BusStopIndex'] +=j
                '''Indicates arrivedAt: BusStopIndex'''
                if VariableDict['arrivedAt'] != VariableDict['BusStopIndex']:
                    #input ()
                    return(VariableDict,True)
    return(VariableDict,False)

import pprint
def PredictionAlgorithmNorthBound(LocationRecord,BusStopsList,HistoricalDataList,VariableDict,PredictionDictList,RouteName):
    '''Apply Prediction Here'''
    '''Logic to be checked'''
    
    PredictionDict = RecordPredictionNorthBound (LocationRecord,VariableDict)
    BusStopsCount = len(BusStopsList)
    if VariableDict['BusStopIndex'] < BusStopsCount-1:
        '''id: 0 to n-1 exists in the HistoricalDataList, according to logic of HistoricalTimeDiffMeanAndStdDev'''
        '''Alternatively, mongodb find('id') can be used'''
        '''Logic to be checked'''
        ArrivedAtTime = LocationRecord['epoch']
        VariableDict = PredictionBasedOnHDataNorthBound(HistoricalDataList,ArrivedAtTime, VariableDict)
		
        #pprint.pprint(VariableDict)

        '''Logic for subsequent BusStop'''
        '''
        VariableCopyDict = {}
        for Variable in VariableDict:
            VariableCopyDict[Variable] = VariableDict[Variable]
        '''
        VariableCopyDict = copy.deepcopy(VariableDict)
        #VariableCopyDict = VariableDict
        
        PredictionTupleList,PredictionMarginTupleList = PredictionForSubsequentStopNorth(HistoricalDataList,BusStopsList,VariableCopyDict)
        
        VariableDict['PredictionTupleList'] = PredictionTupleList
        VariableDict['PredictionMarginTupleList'] = PredictionMarginTupleList

        '''Logic for subsequent BusStop'''
        #pprint.pprint(VariableDict)
        #input()

    '''Logic to be checked'''
    PredictionDictList.append(PredictionDict)
    VariableDict['arrivedAt'] = VariableDict['BusStopIndex']
    #t_j_m1 = LocationRecord ['epoch']
    #j_m1 = BusStopIndex
    if VariableDict['arrivedAt'] < BusStopsCount-1:
        VariableDict['arrivingAt'] = VariableDict['arrivedAt'] + 1
    else:
        VariableDict['arrivingAt'] = -1
        '''In this case prediction must not happen'''
    VariableDict['BusStopIndex'] +=1
    
    return (VariableDict, PredictionDictList)




def RecordPredictionNorthBound (LocationRecord,VariableDict):
    PredictionDict = {}
    PredictionDict['id'] = VariableDict['BusStopIndex']
    PredictionDict['TActual'] = LocationRecord['epoch']
    
    #PredictionDict['TPredicted'] = []
    #PredictionDict['TPredictionMargin'] = []
    
    if VariableDict['t_j_p1_predicted'] != -1:
        
        if LocationRecord['epoch'] >= VariableDict['t_j_p1_predictedL'] and LocationRecord['epoch'] <= VariableDict['t_j_p1_predictedH']:
            PredictionDict['WithInRange'] = True
        else:
            PredictionDict['WithInRange'] = False
        
        PredictionDict['TError'] = VariableDict['t_j_p1_predicted'] - LocationRecord['epoch']
        PredictionDict['TPredicted'] = VariableDict['t_j_p1_predicted']
        PredictionDict['TPredictionMargin'] = (VariableDict['t_j_p1_predictedH'] - VariableDict['t_j_p1_predictedL'])/2
        #PredictionDictList.append(PredictionDict)

        '''For sub BusStop'''
        PredictionDict['PredictionTupleList'] = VariableDict['PredictionTupleList']
        PredictionDict['PredictionMarginTupleList'] = VariableDict['PredictionMarginTupleList']
        VariableDict['PredictionTupleList'] = []
        VariableDict['PredictionMarginTupleList'] = []

    return(PredictionDict)

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


def PredictionBasedOnHDataNorthBound(HistoricalDataList,ArrivedAtTime, VariableDict):
    w_pt = 1
    w_ps = 0
    if HistoricalDataList[VariableDict['BusStopIndex']]['T_pt_Available'] == True:
        
        w_pt = HistoricalDataList[VariableDict['BusStopIndex']]['w_pt']

        if HistoricalDataList[VariableDict['BusStopIndex']]['F_ps_Available'] == True and (VariableDict['j_m1'] == (VariableDict['BusStopIndex'] - 1)):
            w_ps = HistoricalDataList[VariableDict['BusStopIndex']]['w_ps']

            diffValue = w_pt * HistoricalDataList[VariableDict['BusStopIndex']]['T_pt_Mean'] + w_ps * HistoricalDataList[VariableDict['BusStopIndex']]['F_ps_Mean'] * (ArrivedAtTime-VariableDict['t_j_m1'])
            STD = HistoricalDataList[VariableDict['BusStopIndex']]['STD']

            VariableDict['t_j_p1_predicted'] = ArrivedAtTime + diffValue

            VariableDict['t_j_p1_predictedL'] = VariableDict['t_j_p1_predicted'] - STD * diffValue /100
            VariableDict['t_j_p1_predictedH'] = VariableDict['t_j_p1_predicted'] + STD * diffValue /100

            VariableDict['t_j_p1_predictedMargin'] = STD * diffValue /100


        else:

            STD = HistoricalDataList[VariableDict['BusStopIndex']]['STD']
            diffValue = HistoricalDataList[VariableDict['BusStopIndex']]['T_pt_Mean']
            VariableDict['t_j_p1_predicted'] = ArrivedAtTime + diffValue
            VariableDict['t_j_p1_predictedL'] = VariableDict['t_j_p1_predicted'] - STD * diffValue /100
            VariableDict['t_j_p1_predictedH'] = VariableDict['t_j_p1_predicted'] + STD * diffValue /100
            VariableDict['t_j_p1_predictedMargin'] = STD * diffValue /100

        VariableDict['t_j_m1'] = ArrivedAtTime
        VariableDict['j_m1'] = VariableDict['BusStopIndex']
    return(VariableDict)
    #return(t_j_p1_predicted,t_j_p1_predictedL,t_j_p1_predictedH,t_j_p1_predictedMargin,t_j_m1,j_m1)


# In[ ]:
def PredictionForSubsequentStopNorth(HistoricalDataList,BusStopsList,VariableCopyDict):
    
    '''VariableCopyDict is used so that the process of prediction of sub stops does not changes the
    VariableDict values'''
    
    BusStopsCount= len(BusStopsList)
    PredictionTupleList =[]
    PredictionMarginTupleList =[]
    
    PredictionTupleList.append((VariableCopyDict['j_m1'] + 1,VariableCopyDict['t_j_p1_predicted']))
    PredictionMarginTupleList.append((VariableCopyDict['j_m1'] + 1,VariableCopyDict['t_j_p1_predictedMargin']))
    
    VariableCopyDict['BusStopIndex'] = VariableCopyDict['j_m1'] + 1
    
    BusStopIndexInitialVal = VariableCopyDict['BusStopIndex']
    
    for PredictionIndex in range(BusStopIndexInitialVal, BusStopsCount-1):
        
        ArrivedAtTime = VariableCopyDict['t_j_p1_predicted']
        #VariableCopyDict = PredictionBasedOnHDataForNorth(PredictionIndex,BusStopsCount,ArrivedAtTime,j_m1,t_j_m1,HistoricalDataList)
        VariableCopyDict['BusStopIndex'] = PredictionIndex
        VariableCopyDict = PredictionBasedOnHDataNorthBound(HistoricalDataList,ArrivedAtTime, VariableCopyDict)
        PredictionTupleList.append((VariableCopyDict['BusStopIndex']+1,VariableCopyDict['t_j_p1_predicted']))
        PredictionMarginTupleList.append((VariableCopyDict['BusStopIndex']+1,VariableCopyDict['t_j_p1_predictedMargin']))
        
    return(PredictionTupleList,PredictionMarginTupleList)

#def GetArrivalStatusSouthBound(BusStopsListSouth,arrivingAt,arrivedAt,BusStopsList,LocationRecord):
def GetArrivalStatusSouthBound(LocationRecord,BusStopsList,VariableDict,RouteName,Dist_TH):
    BusStopsCount = len (BusStopsList)
    for j in range(0,3):
        if BusStopsCount-VariableDict['BusStopIndex']-1-j >=0:
            DistanceFromStop = mydistance(LocationRecord['Latitude'],LocationRecord['Longitude'],BusStopsList[BusStopsCount-VariableDict['BusStopIndex']-1-j]['Location'][0],BusStopsList[BusStopsCount-VariableDict['BusStopIndex']-1-j]['Location'][1])
            if DistanceFromStop < Dist_TH:
                VariableDict['BusStopIndex'] +=j
                '''Indicates arrivedAt: BusStopCount - 1 - BusStopIndex'''
                if VariableDict['arrivedAt'] != BusStopsCount - 1 - VariableDict['BusStopIndex']:
                    return(VariableDict,True)
                
    return(VariableDict,False)


# In[ ]:


#def PredictionAlgorithmForSouthBound(BusStopIndex,BusStopsListSouth,LocationRecord,t_j_m1_s_predicted,t_j_m1_s_predictedL,t_j_m1_s_predictedH,arrivingAt,arrivedAt,t_j_p1_s,j_p1_s,HistoricalDataList):
#                                   (BusStopIndex,BusStopsList,LocationRecord,t_j_p1_predicted,t_j_p1_predictedL,t_j_p1_predictedH, arrivingAt, arrivedAt, t_j_m1, j_m1, HistoricalDataList)
import copy
def PredictionAlgorithmSouthBound(LocationRecord,BusStopsList,HistoricalDataList,VariableDict,PredictionDictList,RouteName):

    '''Apply Prediction Here'''
    PredictionDict = RecordPredictionSouthBound(LocationRecord,VariableDict,BusStopsList)
    BusStopsCount = len(BusStopsList)
    if BusStopsCount - 1 - VariableDict['BusStopIndex'] > 0:
        ArrivedAtTime = LocationRecord['epoch']
        VariableDict = PredictionBasedOnHDataSouthBound(HistoricalDataList,ArrivedAtTime, VariableDict,BusStopsList)

        '''Logic for subsequent BusStop'''
        '''
        VariableCopyDict = {}
        for Variable in VariableDict:
            VariableCopyDict[Variable] = VariableDict[Variable]
        '''
        VariableCopyDict = copy.deepcopy(VariableDict)
        #VariableCopyDict = VariableDict
        PredictionTupleList,PredictionMarginTupleList = PredictionForSubsequentStopSouth(HistoricalDataList,BusStopsList,VariableCopyDict)
        
        VariableDict['PredictionTupleList'] = PredictionTupleList
        VariableDict['PredictionMarginTupleList'] = PredictionMarginTupleList

        '''Logic for subsequent BusStop'''
        
    '''Apply Prediction Here'''
    PredictionDictList.append(PredictionDict)
    #t_j_p1_s = LocationRecord['epoch']
    #j_p1_s = BusStopsCount -1 - BusStopIndex
            
    VariableDict['arrivedAt'] = BusStopsCount - 1 - VariableDict['BusStopIndex']
    if VariableDict['arrivedAt'] > 0:
        VariableDict['arrivingAt'] = VariableDict['arrivedAt'] - 1
    else:
        VariableDict['arrivingAt'] = -1
        '''In this case prediction must not happen'''
    VariableDict['BusStopIndex'] +=1
    #print (arrivedAt,arrivingAt)
    #input ()
    #break
    return(VariableDict, PredictionDictList)
    #return(t_j_m1_s_predicted,t_j_m1_s_predictedL,t_j_m1_s_predictedH,BusStopIndex,arrivingAt,arrivedAt,j_p1_s,t_j_p1_s)

    #return(t_j_p1_predicted,t_j_p1_predictedL,t_j_p1_predictedH,BusStopIndex,arrivingAt,arrivedAt,t_j_m1,j_m1)


# In[ ]:


#def RecordPredictionForSouth(BusStopIndex, LocationRecord, t_j_m1_s_predicted,t_j_m1_s_predictedL,t_j_m1_s_predictedH,BusStopsListSouth):
    #RecordPredictionForNorth (BusStopIndex,LocationRecord,t_j_p1_predicted,t_j_p1_predictedL,t_j_p1_predictedH)
def RecordPredictionSouthBound(LocationRecord,VariableDict,BusStopsList):
    BusStopsCount = len (BusStopsList)
    PredictionDict = {}
    PredictionDict['id'] = BusStopsCount - 1 - VariableDict['BusStopIndex']
    PredictionDict['TActual'] = LocationRecord['epoch']
    #PredictionErrorDict['ActualTime'].append((BusStopsCount - 1 - BusStopIndex,LocationRecord['epoch']))

    if VariableDict['t_j_m1_s_predicted'] != -1:

        #print('Prediction Accuracy measure:')
        if LocationRecord['epoch'] >= VariableDict['t_j_m1_s_predictedL'] and LocationRecord['epoch'] <= VariableDict['t_j_m1_s_predictedH']:
            #print('Arrived within predicted time range')
            #PredictionErrorDict['WithInMarginCount'] += 1
            PredictionDict['WithInRange'] = True
        else:
            PredictionDict['WithInRange'] = False

        PredictionDict['TError'] = VariableDict['t_j_m1_s_predicted'] - LocationRecord['epoch']
        PredictionDict['TPredicted'] = VariableDict['t_j_m1_s_predicted']
        PredictionDict['TPredictionMargin'] = (VariableDict['t_j_m1_s_predictedH'] - VariableDict['t_j_m1_s_predictedL'])/2
        #PredictionDictList.append(PredictionDict)

        '''For sub BusStop'''
        PredictionDict['PredictionTupleList'] = VariableDict['PredictionTupleList']
        PredictionDict['PredictionMarginTupleList'] = VariableDict['PredictionMarginTupleList']
        VariableDict['PredictionTupleList'] = []
        VariableDict['PredictionMarginTupleList'] = []

    return(PredictionDict)


# In[ ]:


#def PredictionBasedOnHDataSouthBound(HistoricalDataList,BusStopsListSouth,BusStopIndex,j_p1_s,t_j_p1_s,LocationRecord): 
def PredictionBasedOnHDataSouthBound(HistoricalDataList,ArrivedAtTime, VariableDict, BusStopsList):
    w_pt = 1
    w_ps = 0
    BusStopsCount = len (BusStopsList)
    #if BusStopsCount - 1 - BusStopIndex > 0:

    if HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['T_pt_Available'] == True:

        w_pt = HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['w_pt']

        if HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['F_ps_Available'] == True and (VariableDict['j_p1_s'] == (BusStopsCount - VariableDict['BusStopIndex'] )):

            w_ps = HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['w_ps']

            diffValue = w_pt * HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['T_pt_Mean'] + w_ps * HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['F_ps_Mean'] * (ArrivedAtTime-VariableDict['t_j_p1_s'])
            STD = HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['STD']

            VariableDict['t_j_m1_s_predicted'] = ArrivedAtTime + diffValue

            VariableDict['t_j_m1_s_predictedL'] = VariableDict['t_j_m1_s_predicted'] - STD * diffValue /100
            VariableDict['t_j_m1_s_predictedH'] = VariableDict['t_j_m1_s_predicted'] + STD * diffValue /100
            VariableDict['t_j_m1_s_predictedMargin'] = STD * diffValue /100
            #print ('Prediction for BusStopIndex: ',BusStopsCount -1 - 1 - BusStopIndex)
            #print ('STD for Prediction: ',STD)
            #print ('w_pt: ', w_pt,'w_ps: ',w_ps)
            #print ('Delta_pt: ', Delta_pt,'Delta_ps: ',Delta_ps)
            #print('STD: ',STD)

            #print ('t_j_m1_s_predicted: ',t_j_m1_s_predicted)
            #print ('t_j_m1_s_predictedL: ',t_j_m1_s_predictedL)
            #print ('t_j_m1_s_predictedH: ',t_j_m1_s_predictedH)

        else:
            STD = HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['STD']
            diffValue = HistoricalDataList[BusStopsCount -1 - 1 - VariableDict['BusStopIndex']]['T_pt_Mean']
            VariableDict['t_j_m1_s_predicted'] = ArrivedAtTime + diffValue
            VariableDict['t_j_m1_s_predictedL'] = VariableDict['t_j_m1_s_predicted'] - STD * diffValue /100
            VariableDict['t_j_m1_s_predictedH'] = VariableDict['t_j_m1_s_predicted'] + STD * diffValue /100

            VariableDict['t_j_m1_s_predictedMargin'] = STD * diffValue /100
            
        VariableDict['t_j_p1_s'] = ArrivedAtTime
        VariableDict['j_p1_s'] = BusStopsCount -1 - VariableDict['BusStopIndex']

    return(VariableDict)
    #return(t_j_m1_s_predicted,t_j_m1_s_predictedL,t_j_m1_s_predictedH,t_j_m1_s_predictedMargin,t_j_p1_s,j_p1_s)
    #return(t_j_p1_predicted,t_j_p1_predictedL,t_j_p1_predictedH,t_j_p1_predictedMargin,t_j_m1,j_m1)

#def PredictionForSubsequentStopNorth(HistoricalDataList,BusStopsList,VariableCopyDict):    
def PredictionForSubsequentStopSouth(HistoricalDataList,BusStopsList,VariableCopyDict):
    
    BusStopsCount = len(BusStopsList)
    PredictionTupleList = []
    PredictionMarginTupleList = []
    
    '''If first predicted is to be added. Add here'''
    
    PredictionTupleList.append      ((BusStopsCount-1-VariableCopyDict['BusStopIndex']-1,VariableCopyDict['t_j_m1_s_predicted']))
    PredictionMarginTupleList.append((BusStopsCount-1-VariableCopyDict['BusStopIndex']-1,VariableCopyDict['t_j_m1_s_predictedMargin']))
    
    
    VariableCopyDict['BusStopIndex'] = VariableCopyDict['BusStopIndex'] + 1 
    #j_p1_s = BusStopsCount -1 - BusStopIndex
    BusStopIndexInitialVal = VariableCopyDict['BusStopIndex']
    
    for PredictionIndex in range(BusStopIndexInitialVal, BusStopsCount-1):
        
        ArrivedAtTime = VariableCopyDict['t_j_m1_s_predicted']
        VariableCopyDict['BusStopIndex'] = PredictionIndex
        VariableCopyDict = PredictionBasedOnHDataSouthBound(HistoricalDataList,ArrivedAtTime, VariableCopyDict, BusStopsList)

        
        PredictionTupleList.append      ((BusStopsCount-1-VariableCopyDict['BusStopIndex']-1,VariableCopyDict['t_j_m1_s_predicted']))
        PredictionMarginTupleList.append((BusStopsCount-1-VariableCopyDict['BusStopIndex']-1,VariableCopyDict['t_j_m1_s_predictedMargin']))
        
    return(PredictionTupleList,PredictionMarginTupleList )
