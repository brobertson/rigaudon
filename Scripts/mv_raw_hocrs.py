#!/usr/bin/python


def rename_hocr_dir(dir_name):
    splits = dir_name.split('_')
    if splits[-1] == 'output' and splits[-2] == 'hocr' and splits[-3] not in ['combined','selected','raw']:
        splits = splits[:-2] + ['raw'] + splits[-2:]
        dir_name = '_'.join(splits)
    return dir_name

import os, sys

for name in os.listdir(sys.argv[1]):
        possible_outer_dir = os.path.join(sys.argv[1], name)
        if os.path.isdir(possible_outer_dir):
            for inner_name in os.listdir(possible_outer_dir):
                possible_inner_dir = os.path.join(possible_outer_dir,inner_name)
                if os.path.isdir(possible_inner_dir):
                    name_out = rename_hocr_dir(possible_inner_dir)
                    if not name_out == possible_inner_dir:
                        os.rename(possible_inner_dir, name_out)
                        #print possible_inner_dir, name_out

