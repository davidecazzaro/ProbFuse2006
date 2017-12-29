#!/usr/bin/env python
# -*- coding: utf-8 -*-

# everything that relates to ProbFuse2006 is in this library.
# Enjoy.


import 	os
import 	random
import 	numpy 		as 		np
from 	itertools	import 	*


# This function reads from the correct input folder the two lists of parameters
# needed to tune ProbFuseAll and ProbFuseJudged's algorithms.
#
# path: the parameters file
#
# RETURNS: X and t, which are the array of segments and % required by ProbFuse
def extract_params(path):
	if not os.path.isfile(path):
		raise Exception("Error: cannot find the param file, you've gave me: "+path)
	fp = open(path)

	# first line: x parameter.
	line = fp.readline().strip()
	# our param file is like x\t=\t[1,2,3,...,n]
	el = line.split('\t')
	# extracts just the parameters (that are like [1, 2, 3, ..., n])
	params = el[2]
	# removes '[' and ']' characters
	params = params[1:-1]
	x = [y.strip() for y in params.split(',')]
	# casting
	x = [int(y) for y in x]

	# second line: t parameter.
	line = fp.readline().strip()
	# our param file is like t\t=\t[1,2,3,...,n]
	el = line.split('\t')
	# extracts just the parameters (that are like [.1, .2, .3, ..., n])
	params = el[2]
	# removes '[' and ']' characters
	params = params[1:-1]
	t = [y.strip() for y in params.split(',')]
	# casting
	t = [float(y) for y in t]

	fp.close()

	return x,t

# This functions prints the documents' score (final output) in the given out path to file
# 
# out: output file
# scores: dict with the following shape {topic: {doc: its_score__within_the_topic}}
#
# RETURNS: nothing.
def print_scores_to_file(out, scores):

	with open(out, 'w') as writer:
		# To properly write down the output, the topics must be ordered from 351 to 400.
		for topic in sorted(scores):
			# docs contains all the docuents inside this particular topic.
			i = 0
			docs = scores[topic]
			lines = []

			# obviously, we want our documents to be ranked from the highest-scored to the lowest one.
			for doc in sorted(docs, key=docs.get, reverse=True)[:1000]:
				lines.append(str(topic)+" Q0 "+doc+" "+str(i)+" "+str(docs[doc])+" ProbFuse2006")
				i+=1

			for line in lines:
				writer.write(line.strip()+"\n")

# Given the dimension of the topics in our data (=1000) and the number of segments we want to split
# our data in, this function computes the segment sizes for each segment.
# Why wouldn't each segment have different lengths? Check the comments in the function if you're interested.
# 
# topic_dim: =1000
# n_segments: the number of segments we split our data in.
#
# RETURNS: a vector of shape [seg1size, seg(n_segments)size] containing the sizes we want.
def compute_segment_sizes(n_segments, topic_dim):
	# Computing the segment sizes. We're assuming that each topic has constant size (=1000 by default).
	# This phase is extra delicate and it required a little reasoning on paper sheets.
	#
	# If "topic_dim/n_segments" (= segment size) is an integer, then we have no problems whatsoever.
	#
	# If "topic_dim/n_segments" is a fractional number, we've got some rounding problems.
	# (i.e. "1000/150" = 6.66666667 = ...?)
	# 
	# We've decided to split the segments as it follows:
	# The decimal part of that ratio will represents the proportion between "larger" segments and "smaller" ones,
	# where with "larger" segments we mean those segments which size will be rounded up (ceiling),
	# and with "smaller" segments we mean those segments which size will be rounded down (floor).
	# Keeping this ratio between larger and smaller sets will give equilibrium between segments sizes
	# and it also will prevent silly bugs, like having empty segments (if we only round up(,
	# or having more segments than we expect (if we only round down).
	# Also, we decide to just create a segment_sizes VECTOR ([size_of_first_seg, size_of_second_seg, ...])
	# and return it for future use, because of a performance (time complexity) factor.
	#
	# EXAMPLE: X=150 segments; 1000/150 --> 6.666... --> 0.66*150 = 100, number of rounded up segments
	# (= segments of size 7); (1-0.66)*150 = 50, number of rounded down segments (= segments of size 6)
	# 
	# Now, this solution would introduce another rounding problem (e.g. 0.66*150 = 99), so, to prevent this mess,
	# we get the correct proportion by remembering the reminder (100), rather than 0.66 (=100/150)

	seg_rough_size 	= topic_dim/n_segments
	rounded_down 	= int(seg_rough_size)
	# this init might look weird, but it will be fixed below if we have rounding problems
	# if we don't have any problems, then it's fair to have rounded_up = rounded_down.
	rounded_up 		= rounded_down
	# ... we should decide how many rounded up and down segments we want.
	# the # of "rounded up" segments is exactly the reminder, following the reasoning done above.
	remainder 		= topic_dim%n_segments

	# if we haven't got any rounding problems, ...
	if not (remainder==0):
		# there's not "rounded_up", really: we just replace the variable to make it easier to compute later.
		rounded_up 	+= 1

	# the following list will be, as discussed, something like: [seg1size, seg2size, ..., seg(n_segments)size]
	segment_sizes 			=	[rounded_up for x in range(remainder)]
	segment_sizes.extend		([rounded_down for x in range(n_segments-remainder)])

	return segment_sizes

# Given the input set (file path to it), the # of segments, the # of training queries and the judged/all algorithm type,
# this function computes the probability p of a document in a segment s to be relevant, for each run and for each segment.
# 
# in_path: relative input path, string
# n_segments: number of segments we want to split the data with
# n_training_topics: how many training topics we've got
# judged: if you want to perform the probFuseJudged algorithm; =False if you want ProbFuseAll
# n_topics: Fixed at 50 for this problem; makes no sense to change this parameter in this application
# topic_dim: Each topic, by default, has 1000 documents. For our project, it makes no sense to change this.
#
# RETURNS: a "probability" dict; shape: {run: {s: p}},
# where p is the probability that a document in segment is relevant (within run)
def compute_probabilities(in_path, n_segments, n_training_topics, judged, n_topics, topic_dim):

	# probability dictionary; shape: {run: {segment: p}},
	# where p is the probability that a document in the segment is relevant (within the run)
	probability_dict = {}
	
	# extracting all the input files from our input directory
	file_list = [f for f in os.listdir(in_path)]
	if len(file_list) != 10:
		raise Exception("Expecting exactly 10 pre-processed files in "+in_path+"/, 1 per run. Got "+len(file_list)+".")

	# sampling n_training_topics amount of topics from our dataset
	# {run1: [topicX, topicY, ..., topicZ]}
	training_topics = {}
	for i in range(1,10+1):
		possible_topics = range(351,400+1)
		random_topics = random.sample(possible_topics, n_training_topics)
		training_topics[i] = random_topics

	# As a reminder, we know that sizes are the same for each run and for each topic
	# (we always get 1000/n_segments), so we need to do this computation just once.
	segment_sizes = compute_segment_sizes(n_segments, topic_dim)

	# for each run
	for file in file_list:
		# extracting the run we're analyizing from the input file:
		# we need run_idx to be an integer index between 0 and 9.
		run_idx = int(file.strip().split('_')[0])
		# initialization for the current run: it must contain a dict itself
		probability_dict[run_idx] = {}
		# counter re-init; they should be like: {topic: [segment1count, segment2count, ...]}
		are_rel 	= {}
		arent_rel 	= {}
		# file path
		file_path = in_path+"/"+file

		# document counters: "how many documents have we scanned in this topic, yet?"
		i=0
		# re-initialize the segment_idx every time we've done a run.
		segment_idx=0

		# For every file (run), we now count all the occurencies of "1"s (relevant) and "0"s (not relevant)
		with open(file_path) as fp:
			for line in fp:
				# extract, strip and get the line from the file
				line = line.strip()
				elements = line.split(' ')

				if not (len(elements)==3):
					raise Exception("Something's wrong in the pre-processed files. I've got a line with "+len(elements)+" elements: "+line)
				
				# Since we've got topics between 351 and 400, the following number will be \in [351,400].
				topic = int(elements[0])
				# since we're training our algorithm, just read the topics that are \in training_topics.
				if (topic in training_topics[run_idx]):
					# Relevance scores can be either 1 (relevant), 0 (not relevant) or -1 (not graded)
					rel_score 	= int(elements[2])
					# If a new topic is encountered, initialize the lists: are_rel[topic] = [seg0(topic)rel_count, ...],
					# where seg0 -> seg1, etc.
					# Also, reset the document counter and the segment counter from zero
					if not topic in are_rel:
						are_rel[topic] 					= np.zeros(n_segments)
						arent_rel[topic] 				= np.zeros(n_segments)
						i=0
						segment_idx=0

					if (rel_score==1):
						are_rel[topic][segment_idx]		+= 1
					if (rel_score==0):
						arent_rel[topic][segment_idx]	+= 1

					# we've added a document to this segment: +1! :D
					i+=1

					# if we've filled this segment, go to the next one and re-initialize the doc counter
					if(i>=segment_sizes[segment_idx]):
						segment_idx+=1
						i=0

		# now that we have the counters, we can compute the probabilities we need,
		# for each possible segment
		for seg in range(n_segments):
			# sum init
			s = 0

			# here's the main difference between ProbFuseAll and ProbFuseJudged:
			if(judged):
				for t in training_topics[run_idx]:
					# It is likely that rel + not_rel will be > 0, or it would mean
					# to have ALL documents unjudged in a fixed segment/topic.
					# rel+not_rel==0 is likely to happen with high X and low t%,
					# so we just stay cautious and avoid dividing by zero.
					if not (are_rel[t][seg] + arent_rel[t][seg]==0):
						s += are_rel[t][seg]/(are_rel[t][seg]+arent_rel[t][seg])
			else:
				for t in training_topics[run_idx]:
					s += are_rel[t][seg]/(segment_sizes[seg])

			# these "+1" are needed to let this dictionary make sense
			# e.g. "{run1: {seg1: 0.123, seg2: 0.321, ...}, ...}"
			# something like {run0: {seg0: ...}, ...} would be less readable in our opinion
			probability_dict[run_idx][seg+1] = s/n_training_topics

	return probability_dict, training_topics

# Given the input files (the documents) and the pre-evaluated probabilities, this function will compute the  
# the scores of all the documents retrieved by the 10 IR models.
# Note that this function will automatically keep track of the segments the documents are in.
# in_path: our input folder
# probabilities: data structure containing the probabilities {run: {segment: P(doc_in_this_segment | this_run)}}
# training_topics: data structure containing which topics are used to perform the training process for each run {run: [topic1, ...]}
# n_segments: how many segments do we split our documents in?
# topic_dim: how much large is a topic? (default: 1000)
#
# RETURNS: a dict "scores" with shape {topic: {doc: its_score__within_the_topic}}
def score_evaluate(in_path, probabilities, training_topics, n_segments, topic_dim):

	file_list = [f for f in os.listdir(in_path)]

	# we assume that file_list has 10 files, at this point;
	# if there was a problem with our input files, we would have noticed by now.

	# output init
	scores = {}
	segment_sizes = compute_segment_sizes(n_segments, topic_dim)
	# for each run:
	for file in file_list:
		# extracting the run we're analyizing from the input file:
		# we need run_idx to be an integer index between 1 and 10.
		run_idx = int(file.strip().split('_')[0])
		
		# file path
		file_path = in_path+"/"+file

		# document counters: "how many documents have we scanned in this topic, yet?"
		i=0
		# re-initialize the segment_idx every time we've done a run.
		segment_idx=1
		# we need to keep track of which topic we're extracting
		current_topic=351
		# For every file (run), we now compute the score for each document
		with open(file_path) as fp:
			# since we use the training topics to train our algorithm, it makes no sense
			for line in fp:

				line = line.strip()
				elements = line.split(' ')
				topic = int(elements[0])
				if not (topic in training_topics[run_idx]):
					doc = elements[1]

					# if we've never encountered this topic, we better initialize the dict
					if not topic in scores:
						scores[topic] = {}
					
					# if the document has never been encountered in this topic, we'll initialize its score.
					if not doc in scores[topic]:
						scores[topic][doc] = 0

					# also, with a new topic, the doc counter and the segment index should be re-initalized
					if(topic!=current_topic):
						i=0
						segment_idx=1
						current_topic = topic

					scores[topic][doc] += probabilities[run_idx][segment_idx]/segment_idx

					# we've added a document to this segment: +1! :D
					i+=1

					# be aware that in this case segment_idx starts at 1 and goes up to n_segments:
					# our segment_sizes is an array, and therefore accepts indexes between 0 and n_segments-1.
					if(i>=segment_sizes[segment_idx-1]):
						segment_idx+=1
						i=0

	return scores

# Our core function: it takes the input path of the 10 runs, the output path where it will write
# its output (which is a TREC-format fused run), the number of segments, the % of topics
# it'll use to train the model and the "judged" parameter to choose whichever algorithm we want.
# 
# All other parameters are fixed parameters that shouldn't be changed (problem requirements).
#
# This function calles the function that computes the probabilities required by the studied paper,
# calls the score evaluation function and, finally, prints the output in the desired out_path/file.
#
# in_path: relative input path, string
# out_path: relative output path, string
# n_segments: number of segments we want to split the data with
# training_perc: how much % do we want to take out for the training process
# judged=True: if you want to perform the probFuseJudged algorithm; =False if you want ProbFuseAll
# n_topics=50: Fixed at 50 for this problem; makes no sense to change this parameter in this application
# topic_dim=1000: Each topic, by default, has 1000 documents. For our project, it makes no sense to change this.
#
# RETURNS: nothing.

def prob_fuse(in_path, out_path, n_segments, training_perc, judged=True, n_topics=50, topic_dim = 1000):

	
	# picking training_perc*n_topics training queries (topics), to train our ProbFuse algorithm.
	n_tr_to = int(n_topics*training_perc)
	# reminder; pr has the following shape: {run: {segment: probability_a_doc_is_in_segment}}
	pr, tr_to = compute_probabilities(in_path, n_segments, n_tr_to, judged, n_topics, topic_dim)
	
	# With these probabilities is now possible to evaluate our scores
	# scores will have the following shape:
	# {topic: {doc: score}}
	sc = score_evaluate(in_path, pr, tr_to, n_segments, topic_dim)

	# and print them out.
	# Printing means saving the output file at out_path with the following format:
	# <N_TOPIC> <Q0> <DOC_NAME> <INV_IDX> <SCORE> <FUSION_NAME>
	print_scores_to_file(out_path, sc)