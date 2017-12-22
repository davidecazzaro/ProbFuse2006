#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file


import os
import random
import numpy as np

# quick check on the relevances: does their folder exist? are there 10 files in there?
def check_relevances_exist(path):
	if not os.path.isdir(path):
		raise Exception("Expecting a folder in input/relevances")
	n_files = len(os.listdir(path))
	if not (n_files==10):
		raise Exception("Expecting 10 files (e.g. 'rel1.txt') in the /relevances folder, got "+str(n_files))

# given the path of a run, returns its size (rows)
def get_run_size(path):
	i=0
	with open(path) as fp:
		for line in fp:
			i+=1
	return i

# This function receives the input folder path, the number of segments and it returns a data structure like:
# {run: {topic: [(this_docum, is_rel, segment)]}}
def extract_relevance(in_path, segments):

	# counts the run we're extracting now
	run_counter = 1
	# our output file; starts like this, since it's a dict in the first place (see function description)
	out_dict = {}
	# extracting all the input files from our input directory
	file_list = [f for f in os.listdir(in_path)]
	if len(file_list) != 10:
		raise Exception("Expecting exactly 10 pre-processed files in "+in_path+"/, 1 per run. Got "+len(file_list)+".")

	# for each run
	for file in file_list:
		# initialization for the current run: it must contain a dict itself
		out_dict[run_counter] = {}

		file_path = in_path+"/"+file
		# getting the size of a segment; ceiling this value to prevent a silly bug
		segment_size = int(get_run_size(file_path)/segments)+1
		
		# topic counter (to check if we've filled a segment, yet)
		i=0
		segment_counter=1

		with open(file_path) as fp:
			for line in fp:
				# extract, strip and get the line from the file
				line = line.strip()
				elements = line.split(' ')

				if not (len(elements)==3):
					raise Exception("Something's wrong in the pre-processed files. I've got a line with "+len(elements)+" elements: "+line)

				topic = int(elements[0])
				document = elements[1]
				rel_score = int(elements[2])

				# if it's the first entry, create an empty list so that we can append the documents of the same topic.
				if not topic in out_dict[run_counter]:
					out_dict[run_counter][topic] = []

				# update on the dictionary: this particular document is/is not relevant for this topic on this segment of this run
				# and it belongs to this particular segment
				out_dict[run_counter][topic].append((document, rel_score, segment_counter))
				
				# we've added a document to this segment: +1
				i+=1

				# if we've filled this segment, then create the new one and re-initialize
				if(i>=segment_size):
					segment_counter+=1
					i=0
		run_counter+=1

	return out_dict


# returns the same data structure we've got in input, but with less topics.
def get_training_slice(dicty, t):
	# since t is the % of the training tuples over the entire set.
	# we know that we have 50 topics, so...
	new_topic_amount = int(50*t)

	if(new_topic_amount<1):
		raise Exception("The t you've selected is too small and now we obtain "+new_topic_amount+" topics to train on")



	# initializing the dict
	training_dicty = {}
	for run in dicty:
		# sampling new_topic_amount of topics from our input dict for each run
		training_dicty[run] = {k: dicty[run][k] for k in random.sample(dicty[run].keys(), new_topic_amount)}

	return training_dicty


def prob_fuse(in_path, out_path, segments, training_perc):

	# put what we have pre-processed from our files to a well-designed data structure,
	# like this: {run: {topic: [(this_docum, is_rel, segment)]}}
	all_relevances = extract_relevance(in_path, segments)
	# only a % of the queries (topics) are used to train the model
	training_relevances = get_training_slice(all_relevances, training_perc)

	# queries; we know that in our application we have 
	q = 50

	# useful for the next init
	init_f		= {k: 0 for k in range(1,segments+1)}
	# fraction of relevant documents over the (relevants + non relevants), init:
	frac_rel 	= {k: init_f for k in range(1,10+1)}

	# evaluate the probabilities for each run
	for run in training_relevances:
		# current_run contains all the topics in its run:
		current_run = training_relevances[run]
		# relevance counters: init (we have one counter for each segment)
		are_rel 	= np.zeros(segments)
		arent_rel 	= np.zeros(segments)

		for topic in current_run:
			# tuples contains the list of the tuples doc/rel/seg within it:
			tuples = current_run[topic]
			for t in tuples:
				# il numero di doc rilevanti in questo segmento (su tutti i training topics tho)
				
				if(t[1] == 1):
					are_rel[t[2]] 	+= 1
				# il numero di doc non rilevanti in questo segmento (idem)
				if(t[1] == 0):
					arent_rel[t[2]] += 1
				# se rel=-1, significa che non è nè l'uno nè l'altro

		# memorizzo i risultati per questa run
		for i in range(1,segments):
			if not (are_rel[i]==0 and arent_rel[i]==0):
				frac_rel[run][i] = (are_rel[i]/(are_rel[i]+arent_rel[i]))/q
	
	# compute and write down the scores
	# implementare probability =  frac_rel/q
	# we'd like to have a data structure like: {doc: #_of_the_segment}
	raise Exception("DONE UNTIL HERE ----")
	doc_segment_dict = fix_data_structure(all_relevances)

	# finally, evaluate scores
	scores = []
	for document in doc_segment_dict:
		scores[document] = sum([x for x in probability[:][doc_segment_dict[document]]])/doc_segment_dict[document]

	# aaand print them out
	print_scores_tofile(out_path, scores)