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

DEBUG = False
USE_KEY = True
KEY = '698781b4164542dfaf716672b22a1f02'
TEST = False

'''Establish connection to API. Check that response is not null or error'''
def get_connection():
    print('\n'+('#'*20) + ' Connect to API ' + ('#'*20)+ "\n")
    params = 'routes'
    api_w_params = api + params
    if USE_KEY:
        global HEADERS
        HEADERS = {'Authorization' : 'Bearer {0}'.format(KEY)}
        response = requests.get(api_w_params,headers=HEADERS)
    else:
        response = requests.get(api_w_params)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

'''Get routes from API, filter by type, output long_name attribute for each'''
#Returns dictionary.  routes = {type: {id:long_name}}
def q1():

    #Get and format api response
    params = 'routes?filter[type]=0,1'
    api_w_params = api + params
    if USE_KEY:
        response = requests.get(api_w_params,headers=HEADERS)
    else:
        response = requests.get(api_w_params)
    formatted_response = json.dumps(response.json(),  indent=4)
    serializedRoutes = json.loads(formatted_response)
    if DEBUG:
        print(formatted_response)

    #Create dictionaries for storing data
    light_rail = {}
    heavy_rail = {}
    routes = {
        0: light_rail,
        1: heavy_rail}
    #Iterate routes received and store each as a dictionary element keyed by its long name
    #Variables used for readability. Could be eliminated for efficiency
    for route in serializedRoutes["data"]:
        type = route["attributes"]["type"]
        long_name = route["attributes"]["long_name"]
        routes[type][route["id"]] = long_name 
    return routes

'''
Get routes from API, sort by # of stops, output most and least with respective number of stops
Output stops with two or more routes intersecting at stop.
'''
#Returns two tuples, two dictionaries, and a list sorted by descending length of associated list.
#least = (stop_name, number_of_Stops) , most = (stop_name, number_of_Stops), stopsByRoute = {route_ID : [stops]}, stopsByName = {stop_Name : [routes]} , [stops]
def q2( routeDict):
    stopsByRoute = {}
    stopsByName = {}
    #API request for each route to filter for stops by route
    for route in routeDict.keys():
        params = 'stops?filter[route]='+route+'&include=route'
        api_w_params = api + params
        if USE_KEY:
            response = requests.get(api_w_params,headers=HEADERS)
        else:
            response = requests.get(api_w_params)
        formatted_response = json.dumps(response.json(),  indent=4)
        serializedStops = json.loads(formatted_response)
        if DEBUG:
            print(formatted_response)
        #For every stop that has a relationship with the current route, add to two dictionaries
        #Create entry for current route 
        stopsByRoute[route] = []
        for stop in serializedStops["data"]:
            name = stop["attributes"]["name"]
            #Add {route ID : current stop}
            stopsByRoute[route].append(name)
            #Create entry for current stop 
            if not stopsByName.get(name):
                stopsByName[name] = []
            #Add {current stop : route ID}
            stopsByName[name].append(route)
    if DEBUG:
        printer.pprint(stopsByRoute)
    #Sort dictionary of routes by the number of stops they have
    sortedByRoute = sorted(stopsByRoute, key=lambda route: len(stopsByRoute[route]), reverse=False)
    #Find the route with the least and most stops
    leastIndex = 0
    leastStop = routeDict[sortedByRoute[leastIndex]]
    leastStopsNum = len(stopsByRoute[sortedByRoute[leastIndex]])
    least = (leastStop, leastStopsNum)
    mostIndex = -1
    mostStop = routeDict[sortedByRoute[mostIndex]]
    mostStopsNum = len(stopsByRoute[sortedByRoute[mostIndex]])
    most = (mostStop, mostStopsNum)
    #Sort stops by how many routes go through them
    sortedByName = sorted(stopsByName, key=lambda stop: len(stopsByName[stop]), reverse=True)
    return least, most, stopsByRoute, stopsByName, sortedByName

'''
Take user input for any two stops from routes in q1, output route connecting two stops
'''
#Returns start_name, stop_name, [path_taken]
def q3( stop1, stop2, stopsByRoute, stopsByName):
    #BFS of Subway routes, rooting at first user input, preventing re-visitng of stops
    searchSpaceOpen = util.Queue()
    visited = []
    endingLines = stopsByName[stop2]
    #Load Queue with root
    searchSpaceOpen.push((stop1, []))
    #While there are edges to explore
    while not searchSpaceOpen.isEmpty():
        cur = searchSpaceOpen.pop()
        curStop = cur[0]
        curStopLines = stopsByName[curStop]
        curPath = cur[1]
        #Find connecting lines between current stop and the goal stop
        intersection = list(set(curStopLines) & set(endingLines))
        #Base case: there is a line that connects current stop to goal stop
        if intersection:
            curPath.append(intersection[0])
            return stop1, stop2, curPath
        #Recursive case: current stop and goal state do not directly connect
        #Explore all children (adjacent) stops of current stop, until one has connecting line to goal
        else:
            if not (curStop in visited):
                visited.insert(0, curStop)
                #Add every adjacent stop on every line to queue to explore
                for line in stopsByName[curStop]:
                    stopIndex = stopsByRoute[line].index(curStop)
                    if stopIndex > 0:
                        newStop1 = stopsByRoute[line][stopIndex-1]
                        if not (newStop1 in visited):
                            newPath1 =curPath.copy()
                            #Only add new lines to path. No need to repeat current line
                            tempIntersection1 = list(set(stopsByName[curStop]) & set(stopsByName[newStop1]))
                            if not (tempIntersection1[0] in newPath1):
                                newPath1.append(tempIntersection1[0])
                            searchSpaceOpen.push((newStop1, newPath1))

                    if stopIndex < len(stopsByRoute[line])-1 :
                        newStop2 = stopsByRoute[line][stopIndex+1]
                        if not (newStop2 in visited):
                            newPath2 =curPath.copy()   
                            #Only add new lines to path. No need to repeat current line   
                            tempIntersection2 = list(set(stopsByName[curStop]) & set(stopsByName[newStop2]))    
                            if not (tempIntersection2[0] in newPath2):                 
                                newPath2.append(tempIntersection2[0])
                            searchSpaceOpen.push((newStop2, newPath2))

def test_q3():
    #Data from Q1 and Q2 needed for Q3. 
    routes = q1()
    routeDict = dict(routes[0], **routes[1])
    least, most, stopsByRoute, stopsByName, sortedByName = q2(routeDict)
    #Test 3 cases
    #Case a: 2 stops on same line
    a_Stop1 = 'Davis'
    a_Stop2 = 'Braintree'
    a_Path = ['Red']
    a_test_Path = q3(a_Stop1, a_Stop2, stopsByRoute, stopsByName)[2]
    if (a_Path == a_test_Path):
        print("Test case a (2 stops on the same line) passed.")
    else:
        print('Expected: ')
        print(a_Path)
        print('Function returned: ')
        print(a_test_Path)
    #Case b: 2 stops on lines that intersect
    b_Stop1 = 'Eliot'
    b_Stop2 = 'South Street'
    b_Path = ['Green-D', 'Green-B']
    b_test_Path = q3(b_Stop1, b_Stop2, stopsByRoute, stopsByName)[2]
    if b_Path == b_test_Path:
        print("Test case b (2 stops on intersecting lines) passed.")
    else:
        print('Expected: ')
        print(b_Path)
        print('Function returned: ')
        print(b_test_Path)
    #Case c: 2 stops must take one or more other lines to connect
    c_Stop1 = 'Milton'
    c_Stop2 = 'Wonderland'
    c_Path = ['Mattapan', 'Red' , 'Orange','Blue']
    c_test_Path = q3(c_Stop1, c_Stop2, stopsByRoute, stopsByName)[2]
    if c_Path == c_test_Path:
        print("Test case c (2 stops requiring 3 or more lines to connect) passed.")
    else:
        print('Expected: ')
        print(c_Path)
        print('Function returned: ')
        print(c_test_Path)


'''
Main function tests API connection, especially important if using a key 
Runs test program or
Calls all three questions individually. 
Remnant of coding one at a time for scheduling. Data storage could be done much better if only a single function
'''
def main():
    #Accept arguments
    parser.add_argument('-u', '--Use_key', type=bool, default=False, help='Enable global boolean to use a key to connect to the API. [True, False] \tDefault: False' )
    parser.add_argument('-k', '--APIkey', type=str, default='698781b4164542dfaf716672b22a1f02', help='Key to connect to the MBTA API. -u True must be included in command. \texample key: 798981a4164542dfaf716772b22a1f02')
    parser.add_argument('-t', '--Test', type=bool, default=False, help='Run test script for solution program, runs default program that allows input otherwise [True, False] \tDefault: False')
    parser.add_argument('-d', '--Debug', type=bool, default=False, help='Run script with debugging data [True, False] \tDefault: False')
    args = parser.parse_args()
    global KEY
    KEY = args.APIkey
    global USE_KEY
    USE_KEY = args.Use_key
    global TEST
    TEST = args.Test
    global DEBUG
    DEBUG = args.Debug

    #Check connection
    if get_connection() == None:
        print("Error connecting the API")
    else:
        print("Successfully connected to MBTA API")
    #Automated testing of program or allow user input
    if TEST:
        #Test
        #No automated testing provided for Q1 and Q2, easily verifiable manualy for the scope of this problem
        print('\n' + ('#'*20) + ' Testing ' + ('#'*20)+ "\n")
        test_q3()
    else:
        #Q1
        print('\n' + ('#'*20) + ' Question 1 ' + ('#'*20)+ "\n")
        routes = q1()
        #Print respective lists of rails to console
        print("Light Rails:\n\t" + '\n\t'.join(list(routes[0].values())))
        print("\nHeavy Rails:\n\t" + '\n\t'.join(list(routes[1].values())))

        #Q2
        print('\n'+('#'*20) + ' Question 2 ' + ('#'*20)+ "\n")
        #Don't need type of each route, combine the two subdictionaries
        routeDict = dict(routes[0], **routes[1])
        least, most, stopsByRoute, stopsByName, sortedByName = q2(routeDict)
        
        print(most[0] + " has the most stops with " + str(most[1]) + " stops. ")
        print( least[0] + " has the fewest stops with " + str(least[1]) + " stops. ")
        print("\nStops that connect two or more subway routes: ")
        #Print stops, option to print associated lines below
        for stop in sortedByName:
            if len(stopsByName[stop]) >= 2:
                print(stop)
                #print(stop + ":\n\t" + '\n\t'.join(stopsByName[stop]))
            else:
                #Because the list is sorted by number of routes, we can stop looking at the first occurence of a single route stop
                break

        #Q3
        #Parse user input
        print("Choose two stops to find a connecting path")
        valid = False
        while not valid:   
            stop1 = input("Choose your starting stop: ")
            stop2 = input("Choose your destination stop: ")
            if (stopsByName.get(stop1) )and (stopsByName.get(stop2)):
                valid = True
            else:
                print("Stops " + stop1 + " " + stop2 + " are not valid.")    
                print("Please choose valid stops from these options:")
                for route in stopsByRoute.keys():
                    print("\n".join(stopsByRoute[route]))         

        print('\n' + ('#'*20) + ' Question 3 ' + ('#'*20)+ "\n")
        start, stop, path = q3(stop1, stop2, stopsByRoute, stopsByName)
        print("\n" + start + " to " + stop + ": " + ', '.join(path))

'''Call main function at start of program'''    
if __name__ == '__main__':
    main()