#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.plotutils import *

def main():
	# options
	show_map_comb = True
	show_map_comb_trec5 = False
	show_probfuse = False

	map_comb_base_input_folder = "input/ten_models"
	map_comb_comb_input_folder = "output/ten_models/20171229_180835"

	# show_map_comb_trec5
	trec5_map_comb_base_input_folder = "input/trec5"
	trec5_map_comb_comb_input_folder = "output/trec5/20171229_115824"

	# change these as needed, used to plot probfuse
	folder_with_res_to_evaluate = "./output/probfuse/"

	trec_eval_command = "./../materialeDelCorso/trec_eval.8.1/trec_eval"
	qrels3_file = "./input/qrels.trec3.txt"
	qrels5_file = "./input/qrels.trec5.txt"
	qrels7_file = "./input/qrels.trec7.txt"

	if show_map_comb_trec5:
		# plotting map_comb
		plot_trec_map_comb(trec5_map_comb_base_input_folder, trec5_map_comb_comb_input_folder, trec_eval_command, qrels5_file, show=True, save=False)

	if show_map_comb:
		# plotting map_comb
		plot_map_comb(map_comb_base_input_folder, map_comb_comb_input_folder, trec_eval_command, qrels7_file, show=True, save=False)

	# plotting each probfuse model combination of t and x
	if(show_probfuse):
		print("Getting all the scores of probfuse")
		scores = get_map_scores_for_probfuse(folder_with_res_to_evaluate, trec_eval_command, qrels7_file)
		plot_each_probfuse_map(scores, sort_by="t")

if __name__ == '__main__':
   main()