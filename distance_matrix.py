import googlemaps
import numpy as np

gmaps = googlemaps.Client(key='AIzaSyAEd2MmkM5dp2gh-r7eZxZpb9AYQoc4ONM')

origins=[[19.0910544, 74.739012],[19.1241695, 74.7399301],[19.1389804, 74.75289780000001]]
destinations = [[19.1503725, 74.6927354],[19.0947047, 74.73388969999999],[19.1092735, 74.7528519]]

results = gmaps.distance_matrix(origins=origins,destinations=destinations)

rows = len(origins)
cols = len(destinations)

dist_matrix = []
duration_matrix = []

for i in range(0,rows):
  dist_matrix.append([])
  for j in range(0,cols):
    dist_matrix[i].append(results['rows'][i]['elements'][j]['distance']['text'])

for i in range(0,rows):
  duration_matrix.append([])
  for j in range(0,cols):
    duration_matrix[i].append(results['rows'][i]['elements'][j]['duration']['text'])

print dist_matrix
print duration_matrix
