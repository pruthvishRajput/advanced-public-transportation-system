# Software requirement

## MongoDB database:
MongoDB is a document database with the scalability and flexibility. It stores data in flexible, JSON-like documents.
Our project uses MongoDB implementation at every stage. One will need a MongoDB server installed into their system to execute this project.
Download MongoDB community server from [here](https://www.mongodb.com/download-center/community)

### Start, Restart, and Stop  the MongoDB server 
- Command to start the MongoDB server
```shell
foo@bar:~$ sudo service mongod start

```

- Command to restart the MongoDB server
```shell
foo@bar:~$ sudo service mongod restart

```

- Command to stop the MongoDB server

```shell
foo@bar:~$ sudo service mongod stop

```

## Python and related libraries
### Option 1: Anaconda Distribution
We recommend that you have python3 version installed on the system, and one may consider downloading Anaconda Distribution, as our project uses Numpy, ScipY, Jupyter Notebook, Sklearn libraries. Download Anaconda Distribution from [here](https://www.anaconda.com/distribution/#download-section)


### Option 2: Install following libraries

The project application is tested on `Python 3.6.8` and `Python 3.5.2`. We recommend that you have a Python3 version installed into your system or may download Python3 from [here](https://www.python.org/downloads/).

#### SciPy, NumPy, Jupyter Notebook
Download link [here](https://scipy.org/install.html)

#### scikit-learn
Download link [here](https://scikit-learn.org/stable/install.html)

#### Pandas
Download link [here](https://pandas.pydata.org/pandas-docs/stable/install.html)

#### Matplotlib
Download link [here](https://matplotlib.org/users/installing.html)

## Other python libraries (Required)
### PyMongo
PyMongo is a Python distribution containing tools for working with MongoDB, and is the recommended way to work with MongoDB from Python. One may consider downloading PyMongo from [here](https://api.mongodb.com/python/current/index.html)
### pytz 
Download link [here](https://pypi.org/project/pytz/)
