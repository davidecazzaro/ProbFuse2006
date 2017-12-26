#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file

import os
import sys
import shutil
import statistics
import datetime


def check_ground_truth_exist(path):
	if not os.path.exists(path):
		raise Exception("Expecting the ground truth file in the /input folder. Check README for filename info.")

# returns a dict with a key for each topic, which has a list of dicts with a key for each document ((0/1) relevance)
# gt = {topic: {doc: rel_weight}}
def extract_ground_truth(path):
	gt = {}
	with open(path) as fp:
		for line in fp:
			line = line.strip()
			# each line has: top_id, q0, doc_id, rel_weight. Therefore:
			el = line.split(' ')

			if len(el) != 4:
				raise Exception("Something is wrong in '"+path+"': "+str(len(el))+" elements found, 4 expected: "+line)
			tid 	= el[0]
			did 	= el[2]
			rel_w 	= el[3]

			if not tid in gt:
				gt[tid] = {}

			gt[tid][did] = rel_w 

	return gt

# this function reads a run and, for each document retuned for each topic, searches for its corresponding ground truth
# and evaluates if the retrieved document is either relevant, not relevant or neither the two options.
# then, this function writes down the results in an output file.
def evaluate_run(run_file, ground_truth, output_file):
	
	with open(run_file) as fp:
		with open(output_file, 'w') as writer:
			for line in fp:
				line = line.strip()
				el = line.split(' ')
				topic_id 	= el[0]
				doc_id 		= el[2]

				if not doc_id in ground_truth[topic_id]:
					relevance = -1 # "i don't know if it's relevant or not"
				else:
					relevance = ground_truth[topic_id][doc_id]
				newline = topic_id+" "+doc_id+" "+str(relevance)
				
				writer.write(newline.strip() + "\n"	)
