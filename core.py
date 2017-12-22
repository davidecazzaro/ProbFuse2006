#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to keep code organized
from lib.prob_fuse_lib import *

def main():
	# define folders used
	input_folder_path = "input/relevances"
	output_folder_path = "output/pf2006"

	# quick check on folder existence and its content
	check_relevances_exist(input_folder_path)

	# x is the number of segmentes
	for x in [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 100, 150, 200, 250, 300, 400, 500]:
			# t is the training set size, as a percentage of the queries
		for t in [.1, .2, .3, .4, .5]:
			# calling the core function
			prob_fuse(input_folder_path, output_folder_path, x, t)
	print()
	print("ProbFuse2006 done! Output files are in '" + output_folder_path + "'")
	

if __name__ == '__main__':
   main()