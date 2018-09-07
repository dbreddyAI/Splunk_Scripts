### Simple script (custom command) to dynamically update a lookup file depending on parameters returned by a search and those configured within an exisitng lookup file. 
### Author: Nathalie Willems
### Jul 2018

import csv
import shutil 
import os 
import time
import splunk.Intersplunk

app_name="mysplunk_app"

app_dir = os.path.join(os.environ["SPLUNK_HOME"], 'etc', 'apps', app_name)

# Get results from Splunk search
results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

# Get parameters from existing lookup file
csv_in = os.path.join(app_dir, 'lookups', 'job_thresholds_prediction.csv')

if os.path.isfile(csv_in):
        with open(csv_in,"r") as f:
                reader = csv.DictReader(f)
                status = list(reader)
f.close()

# Return search results to Splunk
splunk.Intersplunk.outputResults(results)

for r in results:
        for s in status:
                if r['Job_name'] == s['Job_name']:
			r['Manual'] = s['Manual']
                        if s['Manual'] == '1':
                                r['Threshold'] = s['Threshold']

# Update the existing lookup file 
headers = results[0].keys()
with open(csv_in, "w") as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        writer.writerows(results)
f.close()

