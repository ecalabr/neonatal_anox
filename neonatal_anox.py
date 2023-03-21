import os
from glob import glob
import nibabel as nib
import numpy as np
import csv
import argparse
from scipy.ndimage import binary_closing, generate_binary_structure
from skimage import morphology


# quantify ADC values in atlas segments
def atlas_quant_adc(data_dir, atlas_dir):

    # define suffixes
    adc_suffix = "DTI_eddy_MD_wm"
    dwi_suffix = "DTI_eddy_trace_wm"

    # get adc maps, DWI, atlases, and labels
    adc_maps = glob(data_dir + f"/*/*{adc_suffix}.nii.gz")
    dwis = [item.replace(f"{adc_suffix}.nii.gz", f"{dwi_suffix}.nii.gz") for item in adc_maps]
    atlases = glob(atlas_dir + "/*.nii.gz")
    atlas_labels = [atlas.rsplit('.nii.gz', 1)[0] + '.csv' for atlas in atlases]
    threshs = [0.0008]  # values may be off by factor of 10^6 depending on your data

    # load atlas data
    atlas_niis = [nib.load(atlas) for atlas in atlases]
    atlas_datas = [atlas_nii.get_fdata() for atlas_nii in atlas_niis]

    # initialize output array
    output = []

    # loop through studies and atlases
    for x, adc_map in enumerate(adc_maps):

        # get accession and initialize output row
        accession = os.path.basename(adc_map).rsplit('_')[0]

        # report
        print("Working on {}: study {} of {}".format(accession, x+1, len(adc_maps)))

        # make header line if x == 0
        if x == 0:
            header = ['accession']
            for y, atlas in enumerate(atlases):
                with open(atlas_labels[y], 'r') as f:
                    reader = csv.reader(f)
                    csv_data = list(reader)
                for line in csv_data[1:]:
                    line = [item.replace(' ', '_') for item in line]
                    for thresh in threshs:
                        thresh = 'ADC_' + str(thresh) + '_vol_uL'
                        label = '_'.join(line[1:]) + '_'
                        header = header + [label + 'median_ADC'] + [label + thresh]
            output.append(header)

        # load image data
        adc_nii = nib.load(adc_map)
        adc_data = adc_nii.get_fdata()
        dwi_data = nib.load(dwis[x]).get_fdata()

        # get acute injury volumes
        acute_injury = np.zeros(np.shape(adc_data) + (len(threshs),))
        for t, thresh in enumerate(threshs):
            # get acute injury volume
            injury = np.logical_and(adc_data > 0., adc_data < thresh)
            # eliminate T2 dark-through
            injury[dwi_data < np.mean(dwi_data[np.nonzero(dwi_data)])] = False
            # smooth acute injury
            struct = generate_binary_structure(3, 2)  # rank 3, connectivity 2
            injury = binary_closing(injury, structure=struct)
            acute_injury[:, :, :, t] = morphology.remove_small_objects(injury, min_size=9, connectivity=3)

        # loop through atlases
        for y, atlas in enumerate(atlases):

            # load atlas labels
            with open(atlas_labels[y], 'r') as f:
                reader = csv.reader(f)
                csv_data = list(reader)

            # start output row
            row = [accession]

            # loop through atlas labels
            for line in csv_data[1:]:
                # get median
                label_data = adc_data[atlas_datas[y] == float(line[0])]  # get adc data within label
                label_data = label_data[label_data > 0.]  # eliminate zero data
                label_data = label_data[label_data < 2000.]  # eliminate CSF data
                row += [np.nanmedian(label_data).tolist()]

                # loop through thresholds
                for t, _ in enumerate(threshs):
                    total_injury = np.squeeze(acute_injury[:, :, :, t])
                    row += [np.count_nonzero(total_injury[atlas_datas[y] == float(line[0])])]

            # append row data to output
            output.append(row)

    # write output
    outfile = os.path.join(data_dir, 'adc_data.csv')
    with open(outfile, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output)

    return outfile


# executed  as script
if __name__ == '__main__':

    # parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_dir', default=None,
                        help="Path to data directory")
    parser.add_argument('-a', '--atlas_dir', default="support_files/labels",
                        help="Path to atlas directory - absolute or relative to script directory")

    # parse arguments
    args = parser.parse_args()

    # check data_dir argument
    assert args.data_dir, "No data directory specified. Use -d or --data_dir."
    assert os.path.isdir(args.data_dir), "No data directory found at {}".format(args.data_dir)

    # handle atlas_dir
    if not os.path.isdir(args.atlas_dir):
        args.atlas_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.atlas_dir)
    assert os.path.isdir(args.atlas_dir), "Atlas directory not found at {}".format(args.atlas_dir)

    # do work
    out1 = atlas_quant_adc(args.data_dir, args.atlas_dir)
