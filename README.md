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
2. Create a Python virtual enviroment and install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Prepare the data
   - *Annotation CSV*: Must contain the columns ```AGI``` and ```Name```
   - *Quantification files*: Directory containing subdirectories for each sample. Each sample directory must have a ```quant.sf``` file with ```Name``` and ```TPM``` columns. The scheme for the sample directory should have the following layout: <genotype>_<line>_<replicate>
    
For more details see Quick Start


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