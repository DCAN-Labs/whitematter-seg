import os
import glob
import argparse
from nipype.interfaces import fsl


parser=argparse.ArgumentParser(
    description='''Converts segmentation to brain mask. The output files will be named sub-*_ses-*_aseg_mask.nii.gz
     and sub-*_ses-*_aseg_mask_dil.nii.gz''')

parser.add_argument('working_directory', type=str, help='folder than contains aseg files, named sub-*_ses-*_aseg.nii.gz')
args=parser.parse_args()

base_dir = args.working_directory
os.chdir(base_dir)

aseg = glob.glob('sub-*_aseg.nii.gz')
aseg.sort()

temp = []
for i in aseg:
    temp.append(i.split('_'))

sub = []
for i in range(len(temp)):
    sub.append(temp[i][0])

ses = []
for i in range(len(temp)):
    ses.append(temp[i][1])


##step 1: dilate aseg to make mask:
for sub, ses in zip(sub, ses):
    anatfile = '{}_{}_aseg.nii.gz'.format(sub,ses)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-bin -dilM -dilM -dilM -dilM -fillh -ero -ero -ero',
                           out_file='{}_{}_aseg_mask_dil.nii.gz'.format(sub,ses))
    maths.run()

    anatfile = '{}_{}_aseg_mask_dil.nii.gz'.format(sub, ses)
    maths = fsl.ImageMaths(in_file=anatfile, op_string='-ero',
                           out_file='{}_{}_aseg_mask.nii.gz'.format(sub, ses))
    maths.run()

