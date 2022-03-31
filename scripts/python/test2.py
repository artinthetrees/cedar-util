import os, sys
import pandas as pd
import json
from cedar.utils import getter, updater, searcher, storer

server_address = "https://resource." + os.environ['CEDAR_HOST']
api_key = "apiKey " + os.environ['CEDAR_API_KEY']

folder_id = None
#folder_id = "https://repo.metadatacenter.org/folders/fa170406-f3e8-4d72-8848-0adcb3be6c63"
instance_path = r"C:\Users\tentner-andrea\project_repositories\cedar-util-test-template.json"


with open(instance_path, 'r') as myfile:
    data=myfile.read()

# parse file
instance = json.loads(data)

storer.store_instance(server_address, api_key, instance, folder_id)
