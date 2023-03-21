# Neonatal anox
Neonatal anox is a script for extracting quantitative acute brain injury volumes from ADC images.

# Installation
The following command will clone a copy of neonatal_anox to your computer using git:
```
git clone https://github.com/ecalabr/neonatal_anox.git
```
Install the required packages listed in requirements.txt:
```
# using pip
pip install -r requirements.txt

# using Conda
conda create --name <env_name> --file requirements.txt
```

# Data setup
This software expects your ADC and DWI image data to be in Nifti format, to have a suffix of "...ADC.nii.gz" and "...DWI.nii.gz" respectively, to be registered to your desired brain atlas using non-linear (diffeomorphic) transform, to have all non-brain tissues masked (zeroed) out, and organized in a specific directory tree structure as described in the next section.

### Directory tree
The following example starts with a parent directory (data_dir, but it could be any valid directory name).

```
data_dir/
```
This is an example of the base directory for all the image data that you want to use. All subdirectories in this folder should contain individual patient image data. 

```
data_dir/123456/
```
This is an example of an individual patient study directory. The directory name is typically a patient ID, but can be any folder name that does not contain the "_" character

```
data_dir/123456/123456_ADC.nii.gz
```
This is an example of a single patient ADC image.

The complete directory tree should look something like this:

```
data_dir
│
└───123456
│   │   123456_ADC.nii.gz
│   │   123456_DWI.nii.gz
│   
└───234567
    │   234567_ADC.nii.gz
    │   234567_DWI.nii.gz
```

### Image filename prefix and suffix
The image file name must start with a prefix, which is typcically the patient ID (and is the same as the patient directory name) followed by a "\_" character and then a suffix, which describes the series. For this script, the suffix of the ADC image must be exactly "ADC.nii.gz" and the suffix of the DWI image must be exactly "DWI.nii.gz". Everything in the filename after the first "\_" character will be treated as the prefix (ID) and everything after will be treated as the suffix.

For example:
```
example-patient-1234_ADC.nii.gz
```
In this case the prefix is "example-patient-1234" and suffix is "ADC". This file would live in a folder that was named the same as the prefix (example-patient-1234/).

### G-zipped requirement
All Nifti files are expected to be g-zipped! Uncompressed nifti files will not work without modifying the code considerably.

# Usage
Once you have completed installtion, converted your ADC data to Nifti format, registered it to an atlas using a diffeomorphic transform, brain-masked/skull-stripped it, and organized it according to the file naming conventions and directory tree structure above, then you can use the following command to extract quantitative region-wise ADC values.
```
python neonatal_anox.py -d /path/to/data_dir
```
Where "/path/to/data_dir" is the absolute path to your main data directory.

The output will be a CSV data file (written to your data_dir) with the filename "adc_data.csv".

### Using a different atlas
This script uses the UNC neonatal brain atlas. If you would like to use a different atlas, simply copy the atlas label file to the support_files/labels directory in the script root. You will also need to include a CSV file (with the same name as your atlas), which maps image values to label names. See the included examples for details of CSV formatting.

## Citation
Please cite the following publication(s) if you use any part of this project for your own work:

#### Manuscript under review, please check back later...