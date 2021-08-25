#!/usr/bin/env python3

import os
import shutil
import subprocess
import argparse
from nipype.interfaces import fsl

parser=argparse.ArgumentParser(
    description='''Converts myelinated and unmyelinated FreeSurfer white matter labels to single white matter labels for 
    left and right hemispheres. The output file will be called <subject_name>_WM_merged.nii.gz ''')

parser.add_argument('sublist', type=str, help='subject list for aseg files that you want to convert')
parser.add_argument('working_directory', type=str, help='folder than contains aseg files, named in the format <subject_name>.nii.gz')
args=parser.parse_args()


base_dir = args.working_directory

sublist= open(args.sublist,'r')
sublist = sublist.read().split('\n')


for i in sublist[0:-1]:
    os.chdir('{}'.format(base_dir))

    if not os.path.exists('./wd'):
        os.mkdir('./wd')

    os.chdir('./wd')

    #extract L and R WM myelinated and unmyelinated labels and binarize:
    ##left:
    anatfile = '{}/{}.nii.gz'.format(base_dir, i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string= '-thr 159 -uthr 159 -bin',
                           out_file='{}_roi159.nii.gz'.format(i))
    maths.run()

    maths = fsl.ImageMaths(in_file=anatfile, op_string= '-thr 161 -uthr 161 -bin',
                           out_file='{}_roi161.nii.gz'.format(i))
    maths.run()

    ##right:
    anatfile = '{}/{}.nii.gz'.format(base_dir, i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string= '-thr 160 -uthr 160 -bin',
                           out_file='{}_roi160.nii.gz'.format(i))
    maths.run()

    maths = fsl.ImageMaths(in_file=anatfile, op_string= '-thr 162 -uthr 162 -bin',
                           out_file='{}_roi162.nii.gz'.format(i))
    maths.run()

    #add L and R binarized segs together:
    ##left:
    anatfile = '{}_roi159.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-add {}_roi161.nii.gz'.format(i),
        out_file='{}_L_WM_bin.nii.gz'.format(i))
    maths.run()

    ##right:
    anatfile = '{}_roi160.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-add {}_roi162.nii.gz'.format(i),
        out_file='{}_R_WM_bin.nii.gz'.format(i))
    maths.run()

    ##full (L and R) wm mask:
    anatfile = '{}_L_WM_bin.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-add {}_R_WM_bin.nii.gz'.format(i),
                           out_file='{}_WM_mask_bin.nii.gz'.format(i))
    maths.run()

    #create reverse binarized wm mask to remove wm from image:
    anatfile = '{}_WM_mask_bin.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-binv'.format(i),
                           out_file='{}_WM_mask_binv.nii.gz'.format(i))
    maths.run()

    #mask out wm from image using binv mask:
    anatfile = '{}/{}.nii.gz'.format(base_dir, i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-mas {}_WM_mask_binv.nii.gz'.format(i),
                           out_file='{}_masked.nii.gz'.format(i))
    maths.run()

    #multipy left and right WM masks by appropriate label value:
    anatfile = '{}_L_WM_bin.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-mul 2'.format(i),
                           out_file='{}_L_WM_final.nii.gz'.format(i))
    maths.run()

    anatfile = '{}_R_WM_bin.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-mul 41'.format(i),
                           out_file='{}_R_WM_final.nii.gz'.format(i))
    maths.run()

    #add wm rois back to masked segmentaion:
    anatfile = '{}_L_WM_final.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-add {}_R_WM_final.nii.gz'.format(i),
                           out_file='{}_WM_final.nii.gz'.format(i))
    maths.run()

    anatfile = '{}_masked.nii.gz'.format(i)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-add {}_WM_final.nii.gz'.format(i),
                           out_file='{}_WM_merged.nii.gz'.format(i))
    maths.run()

    #move final file up one directory
    shutil.move('{}_WM_merged.nii.gz'.format(i), '{}/{}_WM_merged.nii.gz'.format(base_dir, i))

    os.chdir('{}'.format(base_dir))