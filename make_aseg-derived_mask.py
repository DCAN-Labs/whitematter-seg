"""
Input the folder path that contains subject asegs to be converted to brain masks.
The output files will be named sub-*_ses-*_aseg_mask.nii.gz and sub-*_ses-*_aseg_mask_dil.nii.gz

Usage:
  make_aseg-derived_mask <aseg_folder> [--dilate]
  make_aseg-derived_mask -h | --help

Options:
  --dilate      Dilate mask so that it is slightly larger than the input aseg
  -h --help     Show this screen.
"""

import os
import glob
from nipype.interfaces import fsl
from docopt import docopt


def make_asegderived_mask(aseg_folder, dilate):

    os.chdir(aseg_folder)
    aseg = glob.glob('sub-*_aseg.nii.gz')
    aseg.sort()

    ## binarize, dilate, fillh, and erode aseg to make mask:
    if dilate == False:
        for aseg_file in aseg:
            anatfile = aseg_file
            maths = fsl.ImageMaths(in_file=anatfile, op_string='-bin -dilM -dilM -dilM -dilM -fillh -ero -ero -ero -ero',
                                   out_file='{}_mask.nii.gz'.format(aseg_file.split('.nii.gz')[0]))
            maths.run()
    else:
        for aseg_file in aseg:
            anatfile = aseg_file
            maths = fsl.ImageMaths(in_file=anatfile, op_string='-bin -dilM -dilM -dilM -dilM -fillh -ero -ero -ero',
                                   out_file='{}_mask_dil.nii.gz'.format(aseg_file.split('.nii.gz')[0]))
            maths.run()


if __name__ == '__main__':
    args = docopt(__doc__)
    make_asegderived_mask(args['<aseg_folder>'], args['--dilate'])