### Purpose: Script to run searches in a loop in Splunk using the Python Splunk-SDK. The search generates encoded models for scaled features using the Splunk ML Toolkit. 
### Author: Nathalie Willems
### Date: Jul 2018

import sys
import csv
import os

app_name = "mysplunk_app"
app_dir = os.path.join(os.environ["SPLUNK_HOME"], 'etc', 'apps', app_name)

EGG_DIR = os.path.join(app_dir, 'bin')

# Read egg file for splunk-sdk modules 
for filename in os.listdir(EGG_DIR):
    if filename.endswith(".egg"):
        sys.path.append(EGG_DIR + filename) 

import splunklib.results as results 
import splunklib.client as client
	
PORT = 8089
USERNAME = user
HOST = host
PASSWORD = password

# Create a Service instance and log in
service = client.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    app=app_name)

# Read in lookup files containing a list of critical jobs to run the search for. This means the jobs are configurable from a lookup file. 
csv_in = os.path.join(app_dir, 'lookups', 'critical_jobs.csv')

if os.path.isfile(csv_in):
        with open(csv_in,"r") as f:
                reader = csv.reader(f)
                temp = list(reader)
                f.close()

jobs = [item for sublist in temp for item in sublist]
jobs_nospace = []

# Remove white spce and colons 
for i in jobs:
    k = i.replace(" ","_")
    t = k.replace(":","")
    jobs_nospace.append(t)

# Enter search parameters and app context 
kwargs_blockingsearch  = {"earliest_time": "-30d@d",
                 "latest_time": "@h",
                 "exec_mode": "blocking",
                 "namespace": app_name,
                 }

# Run the searches
for j,k in zip(jobs[1:],jobs_nospace[1:]):
        print "Starting search for job: %s" % j
        searchquery_blocking = " search index=jobs_index Job_name=\"%s\" Job_Status=Finished | convert num(Duration), num(Delay)" \
        " | bin span=1h _time | stats avg(Duration) as avg_DURATION avg(Delay) as avg_DELAY by _time, Job_name ]"\
        " | fit StandardScaler  avg_DURATION, avg_DELAYinto logreg_%s_StandardScaler" % (j, k) 

        print "Wait for the search to finish..."

        # A blocking search returns the job's SID when the search is done
        search = service.jobs.create(searchquery_blocking, **kwargs_blockingsearch)

        print "...done!\n"

        # Get properties of the job
        print "Search job properties"
        print "Search job ID:        ", search["sid"]
        print "The number of events: ", search["eventCount"]
        print "The number of results:", search["resultCount"]
        print "Search duration:      ", search["runDuration"], "seconds"
        print "This job expires in:  ", search["ttl"], "seconds"
	
	


