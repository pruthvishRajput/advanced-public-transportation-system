from pymongo import     MongoClient
import math
import pprint
import optparse
import numpy

con = MongoClient()

def HistoricalWeights(SingleTripDelInfo,RouteName):
	'''SingleTripDelInfo: Trip for which prediction is made and is to be removed in historical computation'''


	'''
	Get all the trips Information in terms of 'TripStartTimeAggregate' for the North bound and South bound, bus-stop list, bus-stop count,trip that would be removed from historical computation, its bound and start hour
	'''
	TripStartTimeAggregate= [Tr['TripStartTimeBound'] for Tr in con [RouteName]['TripStartTimeAggregate'].find()]
	
	'''Get busstops list for North bound'''
	BusStopsList = [BusStop for BusStop in con[RouteName]['BusStops.NorthBound'].find().sort([('id',1)])]

	BusStopsCount = len (BusStopsList)
	Bound = TripStartTimeAggregate[0][0][1]

	SingleTripDelInfoRecord = [Records for Records in  con[RouteName]['TripInfo'].find({'SingleTripInfo':SingleTripDelInfo})]
	DelBound = SingleTripDelInfoRecord[0]['Bound']
	DelStartHour = SingleTripDelInfoRecord[0]['TripStartHour']

	IterateThroughAggregrateTrips(SingleTripDelInfo, DelBound, DelStartHour, TripStartTimeAggregate, BusStopsList, BusStopsCount, Bound, RouteName)



def IterateThroughAggregrateTrips(SingleTripDelInfo, DelBound, DelStartHour, TripStartTimeAggregate, BusStopsList, BusStopsCount, Bound, RouteName):
	'''
	
	'''
	'''Iterate through aggregrate trips and compute historical weigths'''
	for StartTimeBoundIndex in range(0,len(TripStartTimeAggregate[0])):
		#SingleTripsInfo = [Records['SingleTripInfo'] for Records in  con[RouteName]['TripInfo'].find({'Bound':TripStartTimeAggregate[0][StartTimeBoundIndex][1],'TripStartHour':TripStartTimeAggregate[0][StartTimeBoundIndex][0],'ConsiderForPrediction':True})]
		SingleTripsInfo = [Records['SingleTripInfo'] for Records in  con[RouteName]['TripInfo'].find({'Bound':TripStartTimeAggregate[0][StartTimeBoundIndex][1],'TripStartHour':TripStartTimeAggregate[0][StartTimeBoundIndex][0],'BusStopRecordExtracted':True})]
		
		'''Remove the 'SingleTripDelInfo' from computation of historical weights'''
		if (TripStartTimeAggregate[0][StartTimeBoundIndex][1] == DelBound) and (TripStartTimeAggregate[0][StartTimeBoundIndex][0] == DelStartHour):
			SingleTripsInfo.remove(SingleTripDelInfo)
		
		'''Initialize the difference list for pt and ps'''
		T_pt_list=[]
		F_ps_list=[]
		for index in range (0,BusStopsCount-1):
			T_pt_list.append([])
			F_ps_list.append([])
		
		TripCount = len (SingleTripsInfo)
		
		if TripStartTimeAggregate[0][StartTimeBoundIndex][1] == 'North':
			T_pt_list, F_ps_list = ComputeHistoricalWeigthsNorth(TripCount, BusStopsCount, T_pt_list, F_ps_list, RouteName, SingleTripsInfo)
		else:
			T_pt_list, F_ps_list = ComputeHistoricalWeigthsSouth(TripCount, BusStopsCount, T_pt_list, F_ps_list, RouteName, SingleTripsInfo)
		
		
		CreateHistoricalDictObjectAndStoreInMongo(T_pt_list, F_ps_list, TripStartTimeAggregate, StartTimeBoundIndex, RouteName)



def ComputeHistoricalWeigthsNorth(TripCount, BusStopsCount, T_pt_list, F_ps_list, RouteName, SingleTripsInfo):
	'''
	
	'''
	for TripIndex in range (0,TripCount):
		for index in range (0,BusStopsCount-1):
			if index==0:
				'''Takes care of special case where index-1 bus-stop does not exists (for first bus-stop)'''
				'''Get location record for index and index +1 bus-stop'''
				BusStopRecord_0 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':index}).limit(1)]
				BusStopRecord_1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':index+1}).limit(1)]
				if (len(BusStopRecord_0)!=0 and len(BusStopRecord_1)!=0):
					'''Compute Difference'''
					Diff_1 = BusStopRecord_1[0]['epoch'] - BusStopRecord_0[0]['epoch']
					T_pt_list[index].append(Diff_1)
					#print(index,TripIndex)
			else:
				'''Get location record for index-1, index and index +1 bus-stop'''
				BusStopRecord_i_m1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':index-1}).limit(1)]
				BusStopRecord_i = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':index}).limit(1)]
				BusStopRecord_i_1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':index+1}).limit(1)]

				'''Compute Difference based on availability of record'''
				if (len(BusStopRecord_i)!=0 and len(BusStopRecord_i_1)!=0):

					Diff_1 = BusStopRecord_i_1[0]['epoch'] - BusStopRecord_i[0]['epoch']
					T_pt_list[index].append(Diff_1)
					#print(index,TripIndex)
					#input()
					if len(BusStopRecord_i_m1) !=0:
						Diff_2 = (BusStopRecord_i_1[0]['epoch'] - BusStopRecord_i[0]['epoch'])/(BusStopRecord_i[0]['epoch'] - BusStopRecord_i_m1[0]['epoch'])
						F_ps_list[index].append(Diff_2)
                            
	return(T_pt_list, F_ps_list)

def ComputeHistoricalWeigthsSouth(TripCount, BusStopsCount, T_pt_list, F_ps_list, RouteName, SingleTripsInfo):
	'''
	
	'''
	for TripIndex in range (0,TripCount):
		for index in range (0,BusStopsCount-1):
			if index==0:
				'''Takes care of special case where index-1 bus-stop does not exists (for first bus-stop)'''
				'''Get location record for BusStopsCount-1-1-index and BusStopsCount-1-index bus-stop'''
				
				BusStopRecord_0 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':BusStopsCount-1-1-index}).limit(1)]
				BusStopRecord_1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':BusStopsCount-1-index}).limit(1)]
				if (len(BusStopRecord_0)!=0 and len(BusStopRecord_1)!=0):
					'''Compute Difference'''
					Diff_1 = BusStopRecord_0[0]['epoch'] - BusStopRecord_1[0]['epoch']
					T_pt_list[BusStopsCount-1-1-index].append(Diff_1)
				#print(BusStopsCount-1-1-index,BusStopsCount-1-index)
			else:
				'''Get location record for BusStopsCount-1-1-index, BusStopsCount-1-index and BusStopsCount-1+1-index bus-stop'''
				BusStopRecord_i_m1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':BusStopsCount-1-1-index}).limit(1)]
				BusStopRecord_i = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':BusStopsCount-1-index}).limit(1)]
				BusStopRecord_i_1 = [BusStopRecord for BusStopRecord in con[RouteName][SingleTripsInfo[TripIndex]+'.BusStopsRecord'].find({'id':BusStopsCount-1+1-index}).limit(1)]
				#print(BusStopsCount-1-index-1,BusStopsCount-1-index,BusStopsCount-1+1-index)
				#input()

				'''Compute Difference based on availability of record'''
				if (len(BusStopRecord_i)!=0 and len(BusStopRecord_i_m1)!=0):
					Diff_1 = BusStopRecord_i_m1[0]['epoch'] - BusStopRecord_i[0]['epoch']
					T_pt_list[BusStopsCount-1-1-index].append(Diff_1)

					if len(BusStopRecord_i_1) !=0:
						Diff_2 = (BusStopRecord_i_m1[0]['epoch'] - BusStopRecord_i[0]['epoch'])/(BusStopRecord_i[0]['epoch'] - BusStopRecord_i_1[0]['epoch'])
						F_ps_list[BusStopsCount-1-1-index].append(Diff_2)

	return(T_pt_list, F_ps_list)
        
def CreateHistoricalDictObjectAndStoreInMongo(T_pt_list, F_ps_list, TripStartTimeAggregate, StartTimeBoundIndex, RouteName):
	'''
	
	'''
	'''Creae DiffMeanStd Dict list and store it in MongoDB'''
	DiffMeanStd = []
	for i in range(0,len(T_pt_list)):

		TimeAvgDict = {}
		TimeAvgDict['id'] = i

		w_pt = -1
		STD = -1

		if len(T_pt_list[i]) != 0:
			D_pt = numpy.asarray(T_pt_list[i])
			T_pt_Mean = numpy.mean(D_pt)
			T_pt_STD = numpy.std(D_pt)
			TimeAvgDict['T_pt_Available']= True
			TimeAvgDict['T_pt_Mean'] = T_pt_Mean
			TimeAvgDict['T_pt_STD'] = T_pt_STD
			#Delta_pt = abs(T_pt_Mean-T_pt_STD)/T_pt_Mean *100
			Delta_pt = (T_pt_STD/T_pt_Mean) *100
			TimeAvgDict['Delta_pt'] = Delta_pt
			w_pt = 1
			STD = w_pt * Delta_pt

		else:
			TimeAvgDict['T_pt_Available']= False


		if len(F_ps_list[i]) != 0:
			D_ps = numpy.asarray(F_ps_list[i])
			F_ps_Mean = numpy.mean(D_ps)
			F_ps_STD = numpy.std(D_ps)
			TimeAvgDict['F_ps_Available']= True
			TimeAvgDict['F_ps_Mean'] = F_ps_Mean
			TimeAvgDict['F_ps_STD'] = F_ps_STD
			#Delta_ps = abs(F_ps_Mean-F_ps_STD)/F_ps_Mean *100
			Delta_ps = (F_ps_STD/F_ps_Mean) *100
			TimeAvgDict['Delta_ps'] = Delta_ps
			if Delta_pt == 0 and Delta_ps == 0:
				w_pt=0.5
				w_ps=0.5
			else:
				w_pt = Delta_ps / (Delta_pt + Delta_ps)
				w_ps = Delta_pt / (Delta_pt + Delta_ps)

			TimeAvgDict['w_ps'] = w_ps
			STD = math.sqrt(math.pow(w_pt,2)*math.pow(Delta_pt,2)+math.pow(w_ps,2)*math.pow(Delta_ps,2))


		else:
			TimeAvgDict['F_ps_Available']= False


		TimeAvgDict['w_pt'] = w_pt
		TimeAvgDict['STD'] = STD

		DiffMeanStd.append(TimeAvgDict)

		#print(DMean/(1000*60), DSTV/(1000*60))
		#print(DMean, DSTV)

	con[RouteName].drop_collection('H.'+str(TripStartTimeAggregate[0][StartTimeBoundIndex][0])+'.'+str(TripStartTimeAggregate[0][StartTimeBoundIndex][1]))
	con[RouteName]['H.'+str(TripStartTimeAggregate[0][StartTimeBoundIndex][0])+'.'+str(TripStartTimeAggregate[0][StartTimeBoundIndex][1])].insert_many(DiffMeanStd)

	#pprint.pprint(DiffMeanStd)
	#input()

