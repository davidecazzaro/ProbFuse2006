
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to combine runs are in this file


import os

# quick check on the relevances: does their folder exist? are there 10 files in there?
def check_relevances_exist(path):
	if not os.path.isdir(path):
		raise Exception("Expecting a folder in input/relevances")
	n_files = len(os.listdir(path))
	if not (n_files==10):
		raise Exception("Expecting 10 files (e.g. 'rel1.txt') in the /relevances folder, got "+str(n_files))

def prob_fuse(in_path, out_path, segments, training_perc):

	# put what we have pre-processed from our files to a well-designed data structure,
	# like this: {run: {segment: {topic: (this_docum, is_rel)}}}
	all_relevances = extract_relevance(in_path)
	# only a % of the queries (topics) are used to train the model
	training_relevances = get_training_slice(all_relevances, training_perc)

	# queries; we know that in our application we have 
	q = 50

	# fraction of relevant documents over the (relevants + non relevants), init:
	frac_rel 	= init_frac_dict()
	# relevance counters
	are_rel 	= init_arerel_dict()
	arent_rel 	= init_arentrel_dict()

	# evaluate the probabilities
	for run in training_relevances:
		current_run = training_relevances[run]
		for segment in current_run:
			current_segment = current_run[segment]
			# il numero di doc rilevanti in questo segmento
			are_rel[run][segment] = len([x for x in current_segment if x[1]==1])
			# il numero di doc non rilevanti in questo segmento
			arent_rel[run][segment] = len([x for x in current_segment if x[1]==0])

			frac_rel[run][segment] += (are_rel[run][segment]/(are_rel[run][segment]+arent_rel[run][segment]))

	# compute and write down the scores
	probability =  frac_rel/q
	
	# we'd like to have a data structure like: {doc: #_of_the_segment}
	doc_dict = fix_data_structure(all_relevances)
	for document in doc_dict:
		scores[document] = sum([x for x in probability[:][doc_dict[document]]])/doc_dict[document]

	print_scores_tofile(out_path, scores)