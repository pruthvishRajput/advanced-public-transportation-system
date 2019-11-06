# advanced-public-transportation-system
This is the demonstration of our work "Advanced Urban Public Transportation System for Indian Scenarios"[1]. It includes the location records of college shuttle bus trips between ISCON, Ahmedabad and PDPU, Gandhinagar. The project also includes the interactive implementation of automatic bus-stop detection and bus arrival time prediction. The location records are available in the `LocationRecords` folder. Further, the code and description for interactive implementation of automatic bus-stop detector and arrival time predictor are available in form of jupyter notebooks (unit-1 to unit-4). The implementation includes data preprocessing, creation of MongoDB database, automatic bus-stop detection, extraction of travel time, and arrival time prediction.

The development is based on open source softwares and libraries such as [MongoDB](https://www.mongodb.com/) and it's python api [pymongo](https://api.mongodb.com/python/current/), [MQTT](mqtt.org) communication using [EMQ broker](http://emqtt.io/) and it's client side API ([eclipse's paho-mqtt](https://www.eclipse.org/paho/clients/dotnet/), [pypi's paho-mqtt](https://pypi.org/project/paho-mqtt/)), machine learning library: [scikit-learn](https://scikit-learn.org), scientific computation library: [scipy](https://scipy.org/), [jupyter notebook](https://jupyter.org/), and android based applications developed in [Android Studio](https://developer.android.com/studio).

# Read documentation related to project
Click [here](https://pruthvishrajput.github.io/advanced-public-transportation-system/docs/)

# Executing this project
The project can be executed either online using Binder or on a local system by installing the required softwares and starting MongoDB services and Jupyter notebook server. 
## Executing this project Online (Using Binder)
This project can be read, executed and interacted on the binder by clicking the badge below. The MongoDB installation and server setup are pre-requisite to start the execution of the project on the binder. Execution of `Unit 0 MongoDB Installation (ONLY for BinderHub)` will install the MongoDB server. Further, the MongoDB server should be kept running by keeping the last cell in the notebook of Unit 0 in running state (More information in unit-0).

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pruthvishRajput/advanced-public-transportation-system/master)

## Executing this project on a local system
The project can be read, executed and interacted on a local system by installing or meeting the software requirements mentioned in `SoftwareRequirement.md`. For executing the project on a local system, the jupyter notebook server and MongoDB server should be started using the commands described below:

- Command to start the Jupyter notebook server:
```shell
foo@bar:~$ jupyter notebook

```

- Command to start the MongoDB server:
```shell
foo@bar:~$ sudo service mongod start

```
- Command to stop the MongoDB server:
```shell
foo@bar:~$ sudo service mongod stop

```
# Reference
- [1] P. Rajput, M. Chaturvedi, and P. Patel, “Advanced urban public transportation system for indian scenarios,” in Proceedings of the 20th International Conference on Distributed Computing and Networking, ICDCN , India, January 04-07, 2019, 2019, pp. 327–336. doi: [10.1145/3288599.3288624](https://dl.acm.org/citation.cfm?id=3288624).

# Cite us
If you use any of the content of this project, we would appreciate citations to the following paper:

- P. Rajput, M. Chaturvedi, and P. Patel, “Advanced urban public transportation system for indian scenarios,” in Proceedings of the 20th International Conference on Distributed Computing and Networking, ICDCN , India, January 04-07, 2019, 2019, pp. 327–336. doi: [10.1145/3288599.3288624](https://dl.acm.org/citation.cfm?id=3288624).
