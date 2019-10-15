from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import numpy as np

con = MongoClient()

def PlotPrediction(SingleTripInfo,RouteName):
	'''
	input: The trip selected for arrival time prediction
	output: plot of the arrival time estimate along with the actual travel time of a bus
	function: Extract the list of arrival time prediction dictionary and plot the arrival time estimate 
			  along with the actual travel time of a bus
	'''
	BusStopLabel=['Pakwaan', 'Guru-Dwara', 'Thaltej', 'Zydus', 'Kargil Petrol Pump','Sola','PDPU']

	BusStopsList = [BusStop for BusStop in con[RouteName]['BusStops.NorthBound'].find().sort([('id',1)])]
	BusStopCount = len (BusStopsList)

	PredictionMeanAtStopAggList =[]
	PredictionMeanAtStopList =[]
	PredictionSTDAtStopList =[]
	PredictionMeanAtStopIndexList =[]
	for Stop in range(BusStopCount):
		PredictionMeanAtStopAggList.append([])

	PredictionDictList = [record for record in con[RouteName][SingleTripInfo+'.PredictionResult_Dist_th_50'].find().sort([('id',1)])]
	ActualTimeList = []
	ActualTimeIndexList = []
	PredictedTimeList = []
	PredictedTimeIndexList = []
	PredictedTimeMarginList = []
	PredictionErrorList =[]
	PredictionMarginTupleList =[]
	PredictionTupleList =[]


	PredictionMeanAtStopAggList =[]
	PredictionMeanAtStopList =[]
	PredictionSTDAtStopList =[]
	PredictionMeanAtStopIndexList =[]	

	for Stop in range(BusStopCount):
		PredictionMeanAtStopAggList.append([])

	fig = plt.figure()
	ax1 = plt.subplot2grid((1,1),(0,0))
	for pr in PredictionDictList:
		#if len(pr) == 3:
		if len(pr) == 3 or len(pr) == 4:
			ActualTimeList.append(pr['TActual'])
			ActualTimeIndexList.append(pr['id'])
			
		else:
			ActualTimeList.append(pr['TActual'])
			ActualTimeIndexList.append(pr['id'])
			PredictedTimeList.append(pr['TPredicted'])
			PredictedTimeMarginList.append(pr['TPredictionMargin'])
			PredictedTimeIndexList.append(pr['id'])
			PredictionErrorList.append(pr['TError'])

			'''New'''
			
			PredictList =       [x[1] for x in pr['PredictionTupleList']]
			PredictIndexList =  [x[0] for x in pr['PredictionTupleList']]
			PredictMarginList = [x[1] for x in pr['PredictionMarginTupleList']]
			
			for PredictionIndex in range(len(pr['PredictionTupleList'])):
				
				PredictionMeanAtStopAggList[pr['PredictionTupleList'][PredictionIndex][0]].append(pr['PredictionTupleList'][PredictionIndex][1])


	for PredictionIndex in range(len(PredictionMeanAtStopAggList)):
		if len(PredictionMeanAtStopAggList[PredictionIndex]):
			PredictionArrayAtIndex = PredictionMeanAtStopAggList[PredictionIndex]
			PredictionArrayAtIndex = np.asarray(PredictionArrayAtIndex)
			PredictionMeanAtStopList.append(np.mean(PredictionArrayAtIndex))
			PredictionSTDAtStopList.append(np.std(PredictionArrayAtIndex))
			PredictionMeanAtStopIndexList.append(PredictionIndex)
	
	#print(PredictionMeanAtStopIndexList,PredictionMeanAtStopList,PredictionSTDAtStopList)
	plt.errorbar(PredictionMeanAtStopIndexList,PredictionMeanAtStopList,PredictionSTDAtStopList,marker='o',linestyle='--',label='Predicted Time',color='g',markerfacecolor='none',capsize=2)
	ax1.plot(ActualTimeIndexList,ActualTimeList,color='r',marker='s',label='Actual Time',markerfacecolor='none')
	#print(ActualTimeIndexList,ActualTimeList)
	ylimit = ax1.get_ylim()
	#print(ylimit)
	yticksList =[]
	yticksLabelList = []
	init_pt = ylimit[0]
	i = 1
	pt = init_pt 
	while pt < ylimit[1]:
		pt += 1000 * 5 * 60
		yticksList.append(pt)
		Unix, ms = divmod(pt,1000)
		yticksLabelList.append(int((pt-init_pt)/(1000*60)))
		#yticksLabelList.append(datetime.fromtimestamp(Unix).strftime('%H_%M_%S'))
	#print(yticksLabelList)    
	plt.yticks(yticksList,yticksLabelList)
	xticksList = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
	xticksLabel = ['B1','B2','B3','B4','B5','B6','B7','M1','M2','M3','M4','M5','M6','M7','B8']

	plt.xticks(xticksList,xticksLabel)	
	#ax1.errorbar(PredictedTimeIndexList,PredictedTimeList,PredictedTimeMarginList,marker='o',linestyle='--',label='Predicted Time')
	#ax1.plot(PredictedTimeIndexList,PredictedTimeList,marker='o',linestyle='--',label='Predicted Time')
	plt.xlabel('Bus-stops',fontsize=12)
	plt.ylabel('Travel time (in minutes)',fontsize=12)
	#plt.xticks(ActualTimeIndexList,BusStopLabel)
	#plt.title('Arrival time prediction for Trip '+SingleTripsInfo[TripIndex])	
	plt.legend(loc='best')
	#plt.grid()
	plt.tight_layout()

	plt.tick_params(axis='both', which='major', labelsize=10)
	plt.tick_params(axis='both', which='minor', labelsize=10)	

	#filename=SingleTripsInfo[TripIndex]+".png"
	#pl.savefig('test.eps', format='eps', dpi=900)	
	#plt.savefig('try.png', format='png', dpi=600)
	plt.show()
	#print(ax1.get_xlim())
	#print(ax1.get_ylim())
	#input()

