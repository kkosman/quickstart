#!/usr/bin/python3

# Imports the Google Cloud client library
from google.cloud import datastore
from datetime import datetime

# Instantiates a client
datastore_client = datastore.Client()

# The kind for the new entity
kind = 'Measure'

x = 0
max = 1000000
while x < max:
	x += 1
	# The name/ID for the new entity
	name = 'M {}'.format(datetime.now())
	# The Cloud Datastore key for the new entity
	task_key = datastore_client.key(kind, name)
	# Prepares the new entity
	task = datastore.Entity(key=task_key)
	task['Date'] = datetime.now()
	task['Temperature'] = 1.1 + x
	task['Humidity'] = 0.9
	task['Light'] = 121.1231

	# Saves the entity
	datastore_client.put(task)

	print('{}/{} \n'.format((x/max)*100,max))
