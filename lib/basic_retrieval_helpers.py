#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file

import os
import sys


# check that the input folder exists
def check_folders_exist(path):
	if not os.path.isdir(path):
		raise Exception("We expect a folder "+path+" which contains the 10 folders with the runs.")

	for i in range(1,10+1):
		if not os.path.isdir(path+"/run"+str(i)):
			raise Exception("Missing folder: "+path+"/run"+str(i))


# return a list with the paths of the ten .res files
def get_res_files(path):
	res_files = []
	for i in range(1,10+1):
		file_list = [f for f in os.listdir(path+"/run"+str(i)) if f.endswith('.res')]
		if len(file_list) != 1:
			raise Exception('There should be only one .res file in each run directory')
		res_files.append( path+"/run"+str(i)+"/"+file_list[0] )
	return res_files


# return a dict with a key for each topic which contains a list with doc_id and scores
def parse_res_file(path_to_file):
	buckets = {} # a dict of lists
	with open(path_to_file) as fp:
		for line in fp:
			line = line.strip()
			# a line contains: topic_id Q0 doc_id rank score model
			elements = line.split(' ')
			topic_id 	= elements[0]
			q0 			= elements[1]
			doc_id 		= elements[2]
			rank 		= int(elements[3]) # note: rank starts from 0
			score 		= float(elements[4]) # python floats are double
			model 		= elements[5]

			extracted_tuple = (doc_id, score)

			if len(elements) != 6:
				raise Exception("Found a line in '"+path_to_file+"' with "+str(len(line))+" elements, 6 expected: "+line )

			if topic_id in buckets:
				buckets[topic_id].append( extracted_tuple )
			else:
				buckets[topic_id] = [ extracted_tuple ]
	return buckets



def parse_terrier_run(run_number):

	return run_number