##Shayna Mallett 
##2/22/2022
##Solutions to MGH Coding Test Questions

#!/usr/bin/python

import json
import requests
import argparse
import pprint
import util

api = 'https://api-v3.mbta.com/'
parser = argparse.ArgumentParser(description='Process cmd line args')
printer = pprint.PrettyPrinter(indent=4)
global DEBUG 
DEBUG = False

'''Establish connection to API. Check that response is not null or error'''
def get_connection():
    print('\n'+('#'*20) + ' Connect to API ' + ('#'*20)+ "\n")
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
    print('\n' + ('#'*20) + ' Question 1 ' + ('#'*20)+ "\n")
    #Get and format api response
    params = 'routes?filter[type]=0,1'
    api_w_params = api + params
    response = requests.get(api_w_params,headers=headers)
    formatted_response = json.dumps(response.json(),  indent=4)
    serializedRoutes = json.loads(formatted_response)
    if DEBUG:
        print(formatted_response)
    #Create dictionaries for storing data
    light_rail = {}
    heavy_rail = {}
    routes = {
        0: light_rail,
        1: heavy_rail
    }
    global routeDict
    routeDict = {}

    #Iterate routes received and store each as a dictionary element keyed by its long name
    #Variables used for readability. Could be eliminated for efficiency
    for route in serializedRoutes["data"]:
        type = route["attributes"]["type"]
        long_name = route["attributes"]["long_name"]
        routes[type][route["id"]] = long_name
        routeDict[route["id"]] = long_name

    #Print respective lists of rails to console
    print("Light Rails:\n\t" + '\n\t'.join(list(routes[0].values())))
    print("\nHeavy Rails:\n\t" + '\n\t'.join(list(routes[1].values())))

    global route_Names 
    route_Names = list(routes[0].keys()) + list(routes[1].keys())
'''
Get routes from API, sort by # of stops, output most and least with respective number of stops
Output stops with two or more routes intersecting at stop.
'''
def q2():
    print('\n' + ('#'*20) + ' Question 2 ' + ('#'*20)+ "\n")
    global stopsByRoute
    global stopsByName 
    stopsByRoute = {}
    stopsByName = {}
    for route in route_Names:
        params = 'stops?filter[route]='+route+'&include=route'
        api_w_params = api + params
        response = requests.get(api_w_params,headers=headers)
        formatted_response = json.dumps(response.json(),  indent=4)
        serializedStops = json.loads(formatted_response)

        if DEBUG:
            print(formatted_response)
        stopsByRoute[route] = []
        for stop in serializedStops["data"]:
            name = stop["attributes"]["name"]
            stopsByRoute[route].append(name)
            if not stopsByName.get(name):
                stopsByName[name] = []
            stopsByName[name].append(route)

    if DEBUG:
        printer.pprint(stopsByRoute)
    sortedByRoute = sorted(stopsByRoute, key=lambda route: len(stopsByRoute[route]), reverse=False)
    leastIndex = 0
    leastStops = len(stopsByRoute[sortedByRoute[leastIndex]])
    mostIndex = -1
    mostStops = len(stopsByRoute[sortedByRoute[mostIndex]])
    print(routeDict[sortedByRoute[mostIndex]] + " has the most stops with " + str(mostStops) + " stops. ")
    print(routeDict[sortedByRoute[leastIndex]] + " has the fewest stops with " + str(leastStops) + " stops. ")

    
    sortedByName = sorted(stopsByName, key=lambda stop: len(stopsByName[stop]), reverse=True)
    print("\nStops that connect two or more subway routes: ")
    for stop in sortedByName:
        if len(stopsByName[stop]) >= 2:
            print(stop + ":\n\t" + '\n\t'.join(stopsByName[stop]))
        else:
            break
 



'''
Take user input for any two stops from routes in q1, output route connecting two stops
'''
def q3():
    print('\n'+('#'*20) + ' Question 3 ' + ('#'*20)+ "\n")
    print("Choose two stops to find a connecting path")
    valid = False
    while not valid:   
        stop1 = input("Choose your starting stop: ")
        stop2 = input("Choose your destination stop: ")
        if (stop1 in stopsByName.keys()) and (stop2 in stopsByName.keys()):
            valid = True
            startingLines = stopsByName[stop1]
            endingLines = stopsByName[stop2]
        else:
            print("Stops " + stop1 + " " + stop2 + " are not valid.")    
            print("Please choose valid stops from these options:")
            for route in stopsByRoute.keys():
                print("\n".join(stopsByRoute[route]))         


    intersection = list(set(startingLines) & set(endingLines))
    if intersection:
        #Base case (Since we can take any of the intersecting lines between the stops, choose first for simplicity)
        print(stop1 + " to " + stop2 + ": " + routeDict[intersection[0]])
    else:
        #Recurse until converging to base case
        finalRoute = [stop1]
        searchSpaceOpen = util.Queue()
        visited = []
        searchSpaceOpen.push((stop1, []))
        while not searchSpaceOpen.isEmpty():
            cur = searchSpaceOpen.pop()
            curStop = cur[0]
            curStopLines = stopsByName[curStop]
            curPath = cur[1]
            intersection = list(set(curStopLines) & set(endingLines))
            if intersection:
                curPath.append(intersection[0])
                print("\n" + stop1 + " to " + stop2 + ": " + ', '.join(curPath))
                break
            else:
                if not (curStop in visited):
                    visited.insert(0, curStop)
                    for line in stopsByName[curStop]:
                        stopIndex = stopsByRoute[line].index(curStop)
                        if stopIndex > 0:
                            newStop1 = stopsByRoute[line][stopIndex-1]
                            if not (newStop1 in visited):
                                newPath1 =curPath.copy()
                                tempIntersection1 = list(set(stopsByName[curStop]) & set(stopsByName[newStop1]))
                                if not (tempIntersection1[0] in newPath1):
                                    newPath1.append(tempIntersection1[0])
                                searchSpaceOpen.push((newStop1, newPath1))

                        if stopIndex < len(stopsByRoute[line])-1 :
                            newStop2 = stopsByRoute[line][stopIndex+1]
                            if not (newStop2 in visited):
                                newPath2 =curPath.copy()      
                                tempIntersection2 = list(set(stopsByName[curStop]) & set(stopsByName[newStop2]))    
                                if not (tempIntersection2[0] in newPath2):                 
                                    newPath2.append(tempIntersection2[0])
                                searchSpaceOpen.push((newStop2, newPath2))
 

'''
Main function tests API connection, especially important if using a key 
Calls all three questions individually. 
Remnant of coding one at a time for scheduling. Data storage could be done much better if only a single function
'''
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