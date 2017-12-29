#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Please run this Python script if you're interested in
# running every single aspect of the project.
# 
# The user can choose to run whichever parts of the project:
# skipping some is an option.
#
# This script is able to:
#         - Run the six base combination tecniques;
#         - Run the pre-processing needed to make ProbFuse work properly
#         - Run the ProbFuse approach with X segmentations and t% training queries;
#         - Run the evaluations on everything done until this point (trec_eval);
#         - Find the best parameter selection (X,t) for ProbFuse and print all the MAPS;
# 
# (0) Steps are skippable and X/t parameters can be given in input via the proper file.

from 	lib.basic_retrieval_helpers 	import 	*
from 	lib.plotutils 					import 	*
from 	lib.preprocessing_lib 			import 	*
from 	lib.prob_fuse_lib 				import 	*
import 	subprocess
import 	pprint
import 	operator
import 	datetime

def main():
	select = -1
	while (select!='0' and select!='1'):
		print("Welcome!")
		print("This script will guide you towards the ProbFuse2006 project.")
		print()
		print()
		print()
		print("Step (1): Running the six base combinations tecniques.")
		print("If you already had done this, you're allowed to skip this step:")
		print("\t0: skip the base combination tecniques;")
		print("\t1: run the six combination tecniques now;")

		select = str(input("Your input: ")).strip()

		if(select!='0' and select!='1'):
			print("--- ERROR: please insert a valid input ---")

	print()
	if (select=='0'):
		print("OK \t\t SKIPPING STEP (1) ---")
		print()
	else:


		print("Computing...")
		start_time = datetime.datetime.now()

		# initalizing in/outs/params
		input_folder 	= "input/ten_models"
		output_folder 	= "output/base_combinations/"
		tmp_folder = output_folder + "/tmp/"
		comb_techniques = [combMNZ, combSUM, combMAX, combMIN, combANZ, combMED]


		check_folders_exist(input_folder)
		# prepare output folder to avoid overwriting or mixing results
		# this will wipe out all previous outputs inside our folder
		clean_out_files(output_folder)
		clean_tmp_files(tmp_folder)
		run_files = get_res_files(input_folder)
		
		tempfilepaths = []
		for filepath in run_files:
			topics_docs_scores = parse_res_file(filepath)

			for topic_id in topics_docs_scores:
				topics_docs_scores[topic_id] = normalize_scores(topics_docs_scores[topic_id], "min_max")
				# aggregates the documents/scores by topic
				tempfilepaths.append( append_entries_to_file_by_topic(topic_id, topics_docs_scores[topic_id], tmp_folder) )

		tempfilepaths = list(set(tempfilepaths)) # remove duplicates from list
		tempfilepaths.sort() # not needed but nicer

		# done reading run entries of all 10 models and aggregating them by topic

		for topic_file in tempfilepaths:
			# the following is a dict {document: [score351, score351, ..., score400]}
			docs_scores_aggregated = parse_aggregated_topic(topic_file)

			# extract topic_id from file name
			topic_id = topic_file.split("/")
			topic_id = topic_id[-1].split(".")
			topic_id = topic_id[0]

			for comb_technique in comb_techniques:
				# apply the desired comb technique to the aggregated scores
				new_run = apply_comb_to_aggregated_docs_scores(docs_scores_aggregated, comb_technique)
				
				# prepare tuple with trec format
				formatted_run = format_as_trec_run(new_run, topic_id)

				# append new_run to file
				append_run_to_res_file(output_folder, comb_technique.__name__, formatted_run)

			# Topic done!

		elapsed_time = datetime.datetime.now() - start_time
		print()
		print("Base tecniques are now done! Output files are in '" + output_folder + "'")
		print("Elapsed time: ", elapsed_time)
		print()
	
	select = -1
	while (select!='0' and select!='2'):
		print("Step (2): Preprocessing files for ProbFuse2006")
		print("If you already had done this, you're allowed to skip this step:")
		print("\t0: skip the base combination tecniques;")
		print("\t2: run preprocessing now;")

		select = str(input("Your input: ")).strip()

		if(select!='0' and select!='2'):
			print("--- ERROR: please insert a valid input ---")

	print()
	if (select=='0'):
		print("OK \t\t SKIPPING STEP (2) ---")
		print()
	else:

		print("Preprocessing files...")
		start_time = datetime.datetime.now()

		# init updates
		input_folder 	= "input/ten_models"
		ground_truth	= "input/qrels.trec7.txt"
		output_folder 	= "output/preprocessed_scores"

		# verifying and extracting inputs
		check_ground_truth_exist(ground_truth)
		# cleaning
		clean_out_files(output_folder)


		# checking/creating output folders
		os.makedirs(os.path.dirname(output_folder+"/"), exist_ok=True)

		# our .res files (obviously) don't have the ground truth for each document extracted.
		# therefore, we must create our own set of input files compatible with the probFuse algorithm.
		# then, we extract the ground truth from the file in a proper data structure.
		gndt = extract_ground_truth(ground_truth)

		# then, we extract all the ten runs, properly, but we're just interested at the couple
		# doc/relevance, rather than its score, etc.
		# therefore, we extract every document returned by the query on a certain topic and we judge it
		# foreach run=1,...,10; the result will be in output/relevance_scores

		# if run_files hasn't been already computed above, must retrieve the inputs again:
		run_files = get_res_files(input_folder)

		for filepath in run_files:

			# removes everything but the number of the run.
			# what we want, for example, is just "1", so that we can give the correct output name just below
			run_name = filepath[20:].split('/')[0]
			# this will write our "new" input file in the output folder, such that it'll be like: topic_id, doc_id, rel/notrel.
			evaluate_run(filepath, gndt, output_folder+"/"+run_name+"_preprocessed.txt")

		elapsed_time = datetime.datetime.now() - start_time
		print()
		print("Preprocessing is done! Output files are in '" + output_folder + "'")
		print("Elapsed time: ", elapsed_time)
		print()

	select = -1
	while (select!='0' and select!='3'):
		print("Step (3): ProbFuse algorithm")
		print("If you already had done this, you're allowed to skip this step;")
		print("As a warning, mind that this step might take some time.")
		print("(also remind that you can modify the X and t parameters in input/params.txt)")
		print("\t0: skip the base combination tecniques;")
		print("\t3: run ProbFuse with the chosen parameters now;")

		select = str(input("Your input: ")).strip()

		if(select!='0' and select!='3'):
			print("--- ERROR: please insert a valid input ---")

	print()
	if (select=='0'):
		print("OK \t\t SKIPPING STEP (3) ---")
		print()
	else:

		print("Computing ProbFuse with the parameters you've chosen, which are...")

		input_folder 	= "output/preprocessed_scores"
		param_folder 	= "input/Xtparams.txt"
		output_folder 	= "output/probfuse/"

		x_choices, t_choices = extract_params(param_folder)

		print()
		print("X: "+str(x_choices))
		print("t: "+str(t_choices))
		print()

		select = input("Ready to go? (press Enter to go) ")
		# quick check on folder existence and its content
		check_relevances_exist(input_folder)
		time_summation = datetime.timedelta()
		# x is the number of segmentes
		for x in x_choices:
			# t is the training set size, as a percentage of the queries
			for t in t_choices:
				# For each ProbFuse configuration, we want to try ProbFuseAll and ProbFuseJudged
				for judge in [True, False]:
					# calling the core function
					if judge:
						string_judge = "ProbFuseJudged"
					else:
						string_judge = "ProbFuseAll"
					start_time 		= datetime.datetime.now()
					print ("Combinining with parameters: N_SEGMENTS="+str(x)+", TRAINING_TOPICS="+str(t*50)+", "+string_judge)
					prob_fuse(input_folder, output_folder+string_judge+"_"+str(x)+"_"+str(t)+".res", x, t, judge)
					elapsed_time 	= datetime.datetime.now() - start_time
					time_summation += elapsed_time

		print()
		print("ProbFuse2006 done! Output files are in '" + output_folder + "'")
		print("Elapsed time: ", time_summation)
		print()
	
	select = -1
	while (select!='0' and select!='4'):
		print("Step (4): Evaluations")
		print("If you already had done this, you're allowed to skip this step;")
		print("REMEMBER: it is mandatory that you've already compiled trec_eval")
		print("\t0: skip the base combination tecniques;")
		print("\t4: evaluate every run done until now (ten runs, base combs and prob fuse);")

		select = str(input("Your input: ")).strip()

		if(select!='0' and select!='4'):
			print("--- ERROR: please insert a valid input ---")

	print()
	if (select=='0'):
		print("OK \t\t SKIPPING STEP (4) ---")
		print()
	else:
		print("Computing...")

		start_time = datetime.datetime.now()
		input_folders	= ["input/ten_models", "output/probfuse", "output/base_combinations"]
		output_folders	= ["output/trec_evals/ten_models/", "output/trec_evals/probfuse/", "output/trec_evals/base_combinations/"]
		ground_truth	= "input/qrels.trec7.txt"

		# this path is required to run this script. Better check if it's there.
		if not os.path.isdir("output/trec_evals"):
			os.makedirs(os.path.dirname("output/trec_evals"), exist_ok=True)

		for i in range(3):
			# Recursive file extract, looks for ".res" files only.
			file_list = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(input_folders[i])) for f in fn if f.endswith('.res')]

			for file in sorted(file_list):
				instruction = "./trec_eval.9.0/trec_eval "+ground_truth+" "+file
				instruction = instruction.strip()
				args = instruction.split(' ')
				result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
				# If we're analyizing the ten runs, it is wise to choose "runX" as name
				# If we don't do this, we can occour in some overwriting
				if (i==0):
					out_file = (file.split('/')[-2])
				# all other cases are ok.
				else:
					out_file = (file.split('/')[-1])[:-4]

				if not os.path.isdir(output_folders[i]):
					os.makedirs(os.path.dirname(output_folders[i]), exist_ok=True)

				f = open(output_folders[i]+out_file+"_eval.txt","w+")
				f.write(result)
				f.close()
		elapsed_time = datetime.datetime.now()-start_time
		print()
		print("Evaluations are done! You can find them in  'output/trec_evals'")
		print("Elapsed time: ", elapsed_time)
		print()

	select = -1
	while (select!='0' and select!='5'):
		print("Step (5): Find the best (X, t, judged) that maximizes the MAP")
		print("(note: this will also print all the MAPS on the shell)")
		print("If you already had done this, you're allowed to skip this step;")
		print("\t0: skip the base combination tecniques;")
		print("\t5: quickly find the best ProbFuse model;")

		select = str(input("Your input: ")).strip()

		if(select!='0' and select!='5'):
			print("--- ERROR: please insert a valid input ---")

	print()
	if (select=='0'):
		print("OK \t\t SKIPPING STEP (5) ---")
		print()
	else:
		print("Computing...")
		
		input_folder 	= "output/trec_evals"

		feature_per_file = {}
		folder_list 	= get_eval_files(input_folder)
		

		for folder in folder_list:

			file_list 	= get_eval_files(folder)
			for file in file_list:
				# removes the useless directory path ("output/trec_evals/whatevs/") and the extension ("_eval.txt")
				# we just want "MODELNAME" to be the index of our dict.
				in_folder_len = len(folder)
				method_name = file[in_folder_len+1:-9]
				feature_per_file[method_name] = extract_features(file)

		# for every evaluation result, let's filter out only the features we're interested in:
		maps = map_filter(feature_per_file)
		
		# PrettyPrinter allows us to read decently the contents of a list or a dict.
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(maps)


		print("The best ProbFuse perfomance can be found in the following model: ")
		maximum = max(maps.items(), key=operator.itemgetter(1))
		print(maximum[0], maximum[1])

		input("Press Enter exit...")


if __name__ == '__main__':
   main()