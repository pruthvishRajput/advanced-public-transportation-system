{
 "cells": [
  {
   "attachments": {
    "BinderBadge.png": {
     "image/png": "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"
    }
   },
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# advanced-public-transportation-system\n",
    "This is the demonstration of our work \"Advanced Urban Public Transportation System for Indian Scenarios\"[1]. It includes the location records of college shuttle bus trips between ISCON, Ahmedabad and PDPU, Gandhinagar. The project also includes the interactive implementation of automatic bus-stop detection and bus arrival time prediction. The location records are available in the `LocationRecords` folder. Further, the code and description for interactive implementation of automatic bus-stop detector and arrival time predictor are available in form of jupyter notebooks (unit-1 to unit-4). The implementation includes data preprocessing, creation of MongoDB database, automatic bus-stop detection, extraction of travel time, and arrival time prediction.\n",
    "\n",
    "The development is based on open source softwares and libraries such as [MongoDB](https://www.mongodb.com/) and it's python api [pymongo](https://api.mongodb.com/python/current/), [MQTT](https://www.mqtt.org) communication using [EMQ broker](http://emqtt.io/) and it's client side API ([eclipse's paho-mqtt](https://www.eclipse.org/paho/clients/dotnet/), [pypi's paho-mqtt](https://pypi.org/project/paho-mqtt/)), machine learning library: [scikit-learn](https://scikit-learn.org), scientific computation library: [scipy](https://scipy.org/), [jupyter notebook](https://jupyter.org/), and android based applications developed in [Android Studio](https://developer.android.com/studio).\n",
    "\n",
    "## Executing this project\n",
    "The project can be executed either online using Binder or on a local system by installing the required softwares and starting MongoDB services and Jupyter notebook server. \n",
    "### Executing this project Online (Using Binder)\n",
    "This project can be read, executed and interacted on the binder by clicking the badge below. The MongoDB installation and server setup are pre-requisite to start the execution of the project on the binder. Execution of `Unit 0 MongoDB Installation (ONLY for BinderHub)` will install the MongoDB server. Further, the MongoDB server should be kept running by keeping the last cell in the notebook of Unit 0 in running state (More information in unit-0).\n",
    "\n",
    "[![BinderBadge.png](attachment:BinderBadge.png)](https://mybinder.org/v2/gh/pruthvishRajput/advanced-public-transportation-system/master)\n",
    "\n",
    "### Executing this project on a local system\n",
    "The project can be read, executed and interacted on a local system by installing or meeting the software requirements mentioned in `SoftwareRequirement.md`. For executing the project on a local system, the jupyter notebook server and MongoDB server should be started using the commands described below:"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- Command to start the Jupyter notebook server:\n",
    "```shell\n",
    "foo@bar:~$ jupyter notebook\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- Command to start the MongoDB server:\n",
    "```shell\n",
    "foo@bar:~$ sudo service mongod start\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- Command to stop the MongoDB server:\n",
    "```shell\n",
    "foo@bar:~$ sudo service mongod stop\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Reference\n",
    "- [1] P. Rajput, M. Chaturvedi, and P. Patel, “Advanced urban public transportation system for indian scenarios,” in Proceedings of the 20th International Conference on Distributed Computing and Networking, ICDCN , India, January 04-07, 2019, 2019, pp. 327–336. doi: [10.1145/3288599.3288624](https://dl.acm.org/citation.cfm?id=3288624).\n",
    "\n",
    "## Cite us\n",
    "If you use any of the content of this project, we would appreciate citations to the following paper:\n",
    "\n",
    "- P. Rajput, M. Chaturvedi, and P. Patel, “Advanced urban public transportation system for indian scenarios,” in Proceedings of the 20th International Conference on Distributed Computing and Networking, ICDCN , India, January 04-07, 2019, 2019, pp. 327–336. doi: [10.1145/3288599.3288624](https://dl.acm.org/citation.cfm?id=3288624).\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
