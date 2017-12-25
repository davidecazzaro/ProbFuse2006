#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file


import os
import random
import numpy as np

# quick check on the relevances: does their folder exist? are there 10 files in there?
# path: contains the path to check (a string, relative path)
def check_relevances_exist(path):
	if not os.path.isdir(path):
		raise Exception("Expecting a folder in input/relevances")
	n_files = len(os.listdir(path))
	if not (n_files==10):
		raise Exception("Expecting 10 files (e.g. 'rel1.txt') in the /relevances folder, got "+str(n_files))

# given the path of a run, returns the sizes of its topics, per topic (rows).
# path: the correct path (string, relative path) of the file to check
def get_topic_sizes(path):
	# again, it is known that we've got 50 topics per run.
	i=np.zeros(50)
	with open(path) as fp:
		for line in fp:
			line = line.strip()
			el = line.split(' ')
			# this "-351" is kind of ugly, but it is needed to deal with the array offset (they start at 0)!
			topic_idx = int(el[0])-351
			i[topic_idx]+=1
	return i

# This function receives the input folder path, the number of segments and it returns a data structure like:
# {run: {topic: {segment: {[(doc, rel)]}}}}
# in_path: the path of the 10 pre-processed runs (a string containing the relative path)
# segments: the number of segments we're supposed to split our data with.
def extract_relevance(in_path, segments):

	# problem parameter:
	n_topics=50
	# counts the run we're extracting now; we can afford to start our counters from 1, since we've got a dict
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
		# getting the size of the topics: each topic has its own size.  
		topic_dims = get_topic_sizes(file_path)
		# computing the segment sizes (which is different \all topic).
		# Ceiling this value is necessary to prevent the creation of unwanted extra segments
		segment_size = [int(x/segments) +1 for x in topic_dims]
		# document counters: "how many documents have we scanned in this topic, yet?"
		i=0
		# re-initialize the segment_idx every time we've done a run.
		# indexing starts at one, since segments conceptually are e.g. "1, 2, ... 400", exploiting the dict feature.
		segment_idx=1

		with open(file_path) as fp:
			for line in fp:
				# extract, strip and get the line from the file
				line = line.strip()
				elements = line.split(' ')

				if not (len(elements)==3):
					raise Exception("Something's wrong in the pre-processed files. I've got a line with "+len(elements)+" elements: "+line)
				
				# Since we've got topics between 351 and 400, the following number will be \in [351,400].
				topic = int(elements[0])
				# This is a document ID, a string.
				document = elements[1]
				# Relevance score can be either 1 (relevant), 0 (not relevant) or -1 (not graded)
				rel_score = int(elements[2])

				# now that we know which 

				# if it's the first entry, create an empty dict.
				# Each entry will be a segment inside that particular topic.
				if not topic in out_dict[run_counter]:
					out_dict[run_counter][topic] = {}
					# if we encounter a new topic, the older one is done.
					# Therefore, we can reset the document counter and the segment index,
					# because we expect to fill the FIRST segment of the next topic.
					# This works because the pre-processed files have their lines sorted by topic.
					i=0
					segment_idx=1

				# if it's the first segment for this topic, create an empty list (list of docs/rel \in that segment).
				# Each entry of the list will be a couple (doc/rel) extracted from this line.
				if not segment_idx in out_dict[run_counter][topic]:
					out_dict[run_counter][topic][segment_idx] = []

				# update on the dictionary: tuple(this particular document, is/is not relevant),
				# on THIS run, for THIS topic on THIS segment
				# this horrible "-351" is needed to fix the offset in our segment_idx: it is a vector,
				# therefore its indexes start at 0
				out_dict[run_counter][topic][segment_idx].append((document, rel_score))
				
				# we've added a document to this segment: +1! :D
				i+=1

				# if we've filled this segment, go to the next one and re-initialize the doc counter
				# this "-351" is awful, but again, it is needed to deal with the offset between topics and a standard array
				if(i>=segment_size[topic-351]):
					segment_idx+=1
					i=0
		run_counter+=1

	return out_dict


# returns the same data structure we've got in input, but with less topics.
# dicty: our data structure to slice
# t: the % of topics we want to give in output
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

# Given the documents (with complete info, such as their segment) and the pre-evaluated probabilities,
# this functions gives in output the scores of all the documents retrieved by the 10 IR models.
# documents: our data structure {run: {topic: [(this_docum, is_rel, segment)]}}
# probabilities: data structure containing the probabilities {run: {segment: P(doc_in_this_segment | this_run(=model))}}
def score_evaluate(documents, probabilities):

	scores = {}
	for run in documents:
		this_run = documents[run]
		for topic in this_run:
			this_topic = this_run[topic]
			scores[topic] = {t[0]: sum(probabilities[:,t[2]-1])/t[2] for t in this_topic}
			#for tupl in this_topic:
			#	scores[topic][tupl[0]] = sum(probabilities[:,tupl[2]-1])/tupl[2]

# Given the training set, the # of segments, the # of training queries and eventually the judged/unjudge algorithm type,
# this function computes the probabilities of a document in a segment x to be relevant, for each run.
# training_set: the training queries in the format {run: {topic: {segment: {[(doc, rel)]}}}}
# n_segments: how many segments each topic is divided in
# n_train_queries: how many training queries we expect to have inside training_set
# prob_judge: if True, we're using the probFuseJudged algorithm; instead, if =False, we're using the probFuseAll approach.
# 
# RETURNS: probabilities, which is a dict with this shape: {run: {segment: probability}},
# where probability is the probability that a given document in a segment k is relevant within the IR engine selected (run)
def compute_probabilities(training_set, n_segments, n_train_queries, prob_judged=True):

	# frac_rel will have the following shape:
	# {run: {segment: prob}}
	probabilities = {}

	if prob_judged:
		# evaluate the probabilities for each run
		for run in training_set:
			# current_run contains all the topics in it:
			current_run = training_set[run]

			# relevance counter: init (we have one counter for each segment inside a particular training topic/query)
			are_rel 	= {}
			# non-relevant counter (# documents judged to be not relevant to the query): init. (same)
			arent_rel	= {}

			# init for the fraction of relevant docs for this run
			# (we have one probability for each segment (for each run))
			probabilities[run] = {}

			for topic in current_run:
				# current_topic contains all the segments in it:
				current_topic = current_run[topic]

				are_rel[topic]		= np.zeros(n_segments)
				arent_rel[topic]	= np.zeros(n_segments)

				for segment in current_topic:
					# tupl contains the [(doc,rel)]-like list of tuples within this segment
					tuples = current_topic[segment]
					# segments go from 1 to n_segments, therefore our counters (are_rel, arent_rel)
					# must have a "-1" offset in their indexes (they go from 0 to n_segments-1).

					# Number of relevant documents within this topic in this particular segment;
					are_rel[topic][segment-1] 	= 	len([t for t in tuples if t[1]==1])
					# Number of non-relevant documents within this topic in this particular segment:
					arent_rel[topic][segment-1] = 	len([t for t in tuples if t[1]==0])

					# this algorithm version ignores the "-1" values (unjudged documents)

			# for each segment, it's time to compute the probabilities for this particular run,
			# as it is described in the paper: average over all the training queries;
			# in the probJudge version, the only difference is in the fraction,
			# in which we relate to |rel|+|non_rel| documents, instead of just the cardinality of the whole segment.
			for i in range(1,n_segments+1):
				s = 0
				# here, t=topic: we iterate for each topic
				for t in are_rel:
					# this is a very unfortunate case, but it may happen, and we just don't wanna divide by 0.
					# unfortunate case = every document of this segment, inside this topic, is unjudged. (rel = "-1")
					if not (are_rel[t][i-1]==0 and arent_rel[t][i-1]==0):
						s += are_rel[t][i-1]/(are_rel[t][i-1] + arent_rel[t][i-1])

				probabilities[run][i] = s/n_train_queries
	
	else:
		# evaluate the probabilities for each run
		for run in training_set:
			# current_run contains all the topics in it:
			current_run = training_set[run]

			# relevance counter: init (we have one counter for each segment inside a particular training topic/query)
			are_rel 				= {}
			# non-relevant counter (# documents judged to be not relevant to the query): init. (same)
			segment_cardinalities	= {}

			# init for the fraction of relevant docs for this run
			# (we have one probability for each segment (for each run))
			probabilities[run] = {}

			for topic in current_run:
				# current_topic contains all the segments in it:
				current_topic = current_run[topic]

				are_rel[topic]					= np.zeros(n_segments)
				segment_cardinalities[topic]	= np.zeros(n_segments)

				for segment in current_topic:
					# tupl contains the [(doc,rel)]-like list of tuples within this segment
					tuples = current_topic[segment]

					# segments go from 1 to n_segments, therefore our counters (are_rel, arent_rel)
					# must have a "-1" offset in their indexes (they go from 0 to n_segments-1).
					# counts ALL the documents inside the segment to comput
					segment_cardinalities[topic][segment-1] = 	len(tuples)
					# Number of relevant documents within this topic in this particular segment;
					are_rel[topic][segment-1] 				= 	len([t for t in tuples if t[1]==1])

			# for each segment, it's time to compute the probabilities for this particular run,
			# as it is described in the paper: average over all the training queries;
			for i in range(1,n_segments+1):
				s = 0
				# here, t=topic: we iterate for each topic
				for t in are_rel:
					s += are_rel[t][i-1]/segment_cardinalities[t][i-1]

				probabilities[run][i] = s/n_train_queries

	return probabilities
	
# Score evaluation. Given all the input and the probabilities we've computed above,
# we give in output the following data structure: {topic: {document: its_score_within_its_topic}}
def score_evaluate(data, probabilities):

	# Creating the output, which is something like described above
	scores = {}
	for run in data:
		# this_run has all the topics in this run
		this_run = data[run]

		for topic in this_run:
			# this_topic has all the segments within this topic
			this_topic = this_run[topic]

			# If this topic hasn't been encountered yet, then instantiate a new, empty, dict
			# which will have the following shape: {doc: prob}
			if not (topic in scores):
				scores[topic] = {}

			for segment in this_topic:
				# tuples has all the tuples within this segment
				tuples = this_topic[segment]

				# iterate over all the tuples we have
				for t in tuples:
					d = t[0]
					# If we've never computed the score for this document (within this particular topic),
					# initialize it at zero.
					# The first score to be added will be at the instruction following the "if" structure.
					if not (d in scores[topic]):
						scores[topic][d] = 0

					scores[topic][d] += probabilities[run][segment]/segment

	return scores

def print_scores_to_file(out, scores):

	with open(out, 'w') as writer:
		# To properly write down the output, the topics must be ordered from 351 to 400.
		for topic in sorted(scores):
			# docs contains all the docuents inside this particular topic.
			i = 0
			docs = scores[topic]
			lines = []

			for doc in sorted(docs, key=docs.get, reverse=True):
				lines.append(str(topic)+" Q0 "+doc+" "+str(i)+" "+str(docs[doc])+" ProbFuse2006")
				i+=1

			for line in lines[:1000]:
				writer.write(line.strip()+"\n")
			

# core function: it takes the input path of the 10 runs, the output path where it will write
# its output (which is a TREC-format fused run), the number of segments and the % of topics
# it'll use to train the model.
# This function formats the data in the desired data structures by calling the above functions,
# computes the probabilities and puts them in a nice data structure, calls the score
# evaluation function and, finally, prints the output in the desired out_path/file
# in_path: relative input path, string
# out_path: relative output path, string
# segments: number of segments we want to split the data with
# training_perc: how much % do we want to take out for the training process

def prob_fuse(in_path, out_path, segments, training_perc, judged=True):

	# put what we have pre-processed from our files to a well-designed data structure,
	# like this: {run: {topic: {segment: [(doc, rel)]}}}
	all_relevances = extract_relevance(in_path, segments)

	# only a % of the queries (topics) are used to train the model
	training_relevances = get_training_slice(all_relevances, training_perc)

	# how much topics (=queries) did we use to the traning process?
	# we know that in our application we have 50 total topics
	# and that only (training_perc)% will be used to train the algorithm
	q = int(50*training_perc)

	probs = compute_probabilities(training_relevances, segments, q, prob_judged=judged)

	# With these probabilities is now possible to evaluate our scores
	# scores will have the following shape:
	# {topic: {doc: score}}
	scores = score_evaluate(all_relevances, probs)

	# and print them out.
	# Printing means saving the output file at out_path with the following format:
	# <N_TOPIC> <Q0> <DOC_NAME> <INV_IDX> <SCORE> <FUSION_NAME>
	print_scores_to_file(out_path, scores)