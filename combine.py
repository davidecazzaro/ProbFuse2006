#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helper functions to keep code organized
from lib.basic_retrieval_helpers import *

def main():

	# check input/ten_models if there are folders "run" from 1 to 10 and get .res files 
	input_folder_path = "input/ten_models"
	check_folders_exist(input_folder_path)
	res_files = get_res_files(input_folder_path)
	
	# for
	topics_docs_scores = parse_res_file(res_files[0])

		# for
	print( normalize_scores(topics_docs_scores["351"], "min_max") )

	# apri ogni cartella il file .res

		# parse ogni riga dividendo per topic e salvando docid e sim (score)

		# per ogni metodo diverso -> normalizza

		# usa i vari metodi comb per generare delle nuove run fuse

	# output un file per ogni tipo di comb con i 50 topic
	# con i doc ordinati con i nuovi score calcolati

	print(parse_terrier_run(8))

if __name__ == '__main__':
   main()