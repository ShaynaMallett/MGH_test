##Shayna Mallett 
##2/22/2022
##Solutions to MGH Coding Test Questions

#!/usr/bin/python

from tkinter import *
import json
import requests
import os

api = 'https://api-v3.mbta.com/docs/swagger/swagger.json'
api_short = 'https://api-v3.mbta.com/docs/swagger/'
key = '698781b4164542dfaf716672b22a1f02'
headers = {'Authorization' : 'Bearer {0}'.format(key)}

def get_connection(use_key):
    if use_key:
        response = requests.get(api,headers=headers)
    else:
        respons = requests.get(api)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None
def q1(use_key):
    if use_key:
        params = 'routes/filter[0]'
        api_w_params = api_short + params
        api_w_params_test = 'https://api-v3.mbta.com/routes/?fields%5Broute%5D=short_name,long_name'
        response = requests.get(api_w_params_test,headers=headers)
        #print(response)
        formatted_response = json.dumps(response.json(), sort_keys=True, indent=4)
        print(formatted_response)

def main():
    use_key = True
    if get_connection(use_key) == None:
        print("Error connecting the API")
    else:
        print("Successfully connected to MBTA API")

    q1(use_key)

'''Call main function at start of program'''    
if __name__ == '__main__':
    main()