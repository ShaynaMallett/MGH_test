# MGH_test
Modified from Broad DSP Engineering Interview Take-Home Test

# Usage
Requirements: json, requests, argparse, pprint
```
python3 solution.py 
```

Option Tag | Description
----------------------- | -----------------------------
-u,--Use_key |Enable global boolean to use a key to connect to the API. [True, False] Default: False
-k, --APIkey |Key to connect to the MBTA API. -u True must be included in command. example key: 798981a4164542dfaf716772b22a1f02')
-t, --Test |Run test script for solution program, runs default program that allows input otherwise [True, False] Default: False
-d, --Debug |Run script with debugging data [True, False] Default: False
   

# Solution explanations
Question 1 

I chose to allow the server to filter results rather than locally to limit the amount of data received. Since the scope of the whole assignment is subway stops, every other type of stop would be excess data that gets ignored or deleted. 

Question 2 

For requests of relationships between stops and routes requires filtering by the relationship before it can be included. Using the route names and IDs from Question 1 I could request all stops and filter by their related routes easily and dynamically, creating dictionaries to associate routes with their stops, and stops with their routes.  

Question 3

I used a BFS algorithm restraining the search space to unvisited stops to prevent cycles. Queue data structure implemented to explore adjacent stops (via all routes) until a path of non-empty intersections of route ID is found between the two input stops. BFS is preferred because we are only looking for an intersection of the routes which are not deep in the tree. 

Notes on improvement: 

Runtime for algorithm is relative to the number of edges each stop has (2 per route at that stop)
In the size of the problem for MBTA, it is easily computable, but for larger systems especially ones with less dense intersections of routes, it would be useful to optimize the algorithm. The API can provide several useful metrics that can be used as heuristics to limit the search space, including lattitudinal/longitudinal proximity and directional information of each line to prevent following dead end branches. 




