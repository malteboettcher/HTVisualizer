# RNA-seq Expression Dashboard

This project provides an interactive web-based dashboard for visualizing RNA-seq gene expression data. It allows users to explore gene expression levels across samples, visualize isoform-specific expression, and export plots in multiple formats.  

## Features

- **Interactive Gene Selection:** Search and select genes from the provided annotation data.  
- **Expression Visualization:** Plot mean and standard deviation (TPM) across sample groups and different isoforms.  
- **Export Options:** Download plots as SVG, PNG, or PDF.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/malteboettcher/HTVisualizer.git
cd HTVisualizer
```
2. Create a Python virtual enviroment and install dependencies. Make sure you have ```Python 3.13+``` installed.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Prepare the data
   - *Annotation CSV*: Must contain the columns ```AGI``` and ```Name```
   - *Quantification files*: Directory containing subdirectories for each sample. Each sample directory must have a ```quant.sf``` file with ```Name``` and ```TPM``` columns. The scheme for the sample directory should have the following layout: ```<genotype>_<line>_<replicate>```
    
For more details see ```Quick Start```


## Usage
Run the Dash application from the command line:
 ```bash
 python main.py --annotation <path_to_annotation_csv> --expression <path_to_quant_dir>
 ```

Optional arguments:
- ```host```: Host to run the app on (default: ```127.0.0.1```)
- ```port```: Port to run the app on (default: ```8050```)
- ```debug```: Enable debug mode

Example:
 ```bash
 python main.py --annotation data/Thalemine_gene_names.csv --expression data/AtRTD3/ --host 0.0.0.0 --port 8080 --debug
 ```

This will start a local web server accessible at ```http://0.0.0.0:8080```.

## Quick Start

If you want to try the dashboard without preparing real RNA-seq data, you can use the provided example data under ```example_data/``` or create your own data.

1. Create Example Annotation CSV
For example create a file example_annotation.csv with the following content:
```
AGI;Name
AT1G01010;GeneA
AT1G01020;GeneB
AT1G01030;GeneC
```

2. Create Example Quantification Data
Create a folder structure like this:
```
example_quant/
├── sample1/
│   └── quant.sf
├── sample2/
│   └── quant.sf
```

Each ```quant.sf``` should be a tab-separated file with columns ```Name``` and ```TPM```. For example:

```example_quant/ko_LL18_1/quant.sf```:
```aiignore
Name	TPM
AT1G01010.1	10
AT1G01010.2	5
AT1G01020.1	7
AT1G01030.1	12
```

```example_quant/ko_LL19_1/quant.sf```:
```aiignore
Name	TPM
AT1G01010.1	8
AT1G01010.2	6
AT1G01020.1	9
AT1G01030.1	11
```
3. Run the Dashboard

```bash
python main.py --annotation example_annotation.csv --expression example_quant/
```

Open your browser at ```http://127.0.0.1:8050``` to explore the dashboard.

You can now select genes from the dropdown and see their expression across ko_LL18_1 and ko_LL19_1. Download the plots using the buttons on the left panel.