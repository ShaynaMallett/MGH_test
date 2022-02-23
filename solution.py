##Shayna Mallett 
##2/22/2022
##Solutions to MGH Coding Test Questions

#!/usr/bin/python

from tkinter import *
import json
import requests
import argparse

api = 'https://api-v3.mbta.com/'
parser = argparse.ArgumentParser(description='Process cmd line args')

'''Establish connection to API. Check that response is not null or error'''
def get_connection():
    print("########Get connection########")
    global headers 
    params = 'routes'
    api_w_params = api + params
    headers = {'Authorization' : 'Bearer {0}'.format(key)}
    response = requests.get(api_w_params,headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

'''Get routes from API, filter by type, output long_name attribute for each'''
def q1():
    print("########Question 1########")
    #Get and format api response
    #Allow API to filter to avoid receiving excess data
    #Note, could request only route long_names, but we are using the rest of the data in q2, q3
    #so we request and store all of it here
    params = 'routes?filter[type]=0,1&include=stop'
    api_w_params = api + params
    response = requests.get(api_w_params,headers=headers)
    formatted_response = json.dumps(response.json(),  indent=4)
    indexed = json.loads(formatted_response)
    print(formatted_response)
    #Create dictionaries for storing data
    #Hashing by route type is unnecessary per instructions,
    #but requires only one, two element dictionary lookup (computationally inexpensive)
    #and will be useful for organizing output
    light_rail = {}
    heavy_rail = {}
    routes = {
        0: light_rail,
        1: heavy_rail
    }

    #Iterate routes received and store each as a dictionary element keyed by its long name
    #Variables used for readability. Could be eliminated for efficiency
    for route in indexed["data"]:
        type = route["attributes"]["type"]
        long_name = route["attributes"]["long_name"]
        routes[type][long_name] = route["id"]

    #Print respective lists of rails to console
    print("Light Rails:")
    print(*list(routes[0].keys()), sep='\n')
    print("\nHeavy Rails:")
    print(*list(routes[1].keys()), sep='\n')

    #route_Names = *list(route[0].keys(), sep=',') + ',' + *list(route[1].keys(), sep=',')
    global routeNames 
    routeNames = ','.join(list(routes[0].values())) +',' + ','.join(list(routes[1].values()))
    
'''
Get routes from API, sort by # of stops, output most and least with respective number of stops
Output stops with two or more routes intersecting at stop.
'''
def q2():
    print("########Question 2########")
    #params = 'routes?filter[type]=0,1&filter[stop]=0,1,2'
    params = 'stops?filter[location_type]=0,1'#filter[route]='+routeNames
    api_w_params = api + params
    print(api_w_params)
    response = requests.get(api_w_params,headers=headers)
    formatted_response = json.dumps(response.json(),  indent=4)
    indexed = json.loads(formatted_response)
    print(formatted_response)
'''
Take user input for any two stops from routes in q1, output route connecting two stops
'''
def q3():
    print("########Question 3########")
    #Dijkstra's shortest path BFS node exploration

def main():
    parser.add_argument('-k', '--APIkey', type=str, default='698781b4164542dfaf716672b22a1f02', help='Key to connect to the MBTA API')
    args = parser.parse_args()
    global key 
    key = args.APIkey

    if get_connection() == None:
        print("Error connecting the API")
    else:
        print("Successfully connected to MBTA API")

    q1()
    q2()
    q3()

'''Call main function at start of program'''    
if __name__ == '__main__':
    main()