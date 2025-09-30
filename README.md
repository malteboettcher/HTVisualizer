# RNA-seq Expression Dashboard

This project provides an interactive web-based dashboard for visualizing RNA-seq gene expression data. It allows users to explore gene expression levels across samples, visualize isoform-specific expression, and export plots in multiple formats.  

## Features

- **Interactive Gene Selection:** Search and select genes from the provided annotation data.  
- **Expression Visualization:** Plot mean and standard deviation (TPM) across sample groups and different isoforms.  
- **Export Options:** Download plots as SVG, PNG, or PDF.

## Installation (from sources)

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
The following conventions are assumed for the application:
   1. Gene/AGI Naming
      - Genes are identified using AGI codes in the annotation CSV and the quantification files.
      - Standard pattern of AGIs:
         ```bash
         AT<ChromosomeNumber>G<GeneNumber>
         ```
      - Example: ```AT1G01010```, ```AT2G02530```,```AT5G12345```
      - Isoforms are appended with .1, .2, etc. in quantification files:
        - ```AT1G01010.1```
        - ```AT1G01010.2```
      - *Assumption*: Every gene in the quantification file can be mapped to the AGI column in the annotation CSV.
   2. Annotation CSV:
      - *Required columns*:
        - ```AGI```: Gene identifier matching the quantification data.
        - ```Name```: human-readable gene name or description
      - *Delimiter*: Semicolon (```;```)
      - *Example*:
      ```aiignore
      AGI;Name
      AT1G01010;GeneA
      AT1G01020;GeneB
      ...
      ```
   3. Quantification File (```quant.sf```)
      - Each sample is represented as a folder containing a ```quant.sf``` file.
      - ```quant.sf``` file must be tab-separated and contain at least the following columns:
        - Name: Isoform identifier (AT1G01010.1)
        - TPM: Expression value
      - Example:
      ```aiignore
      Name	TPM
      AT1G01010.1	5
      AT1G01010.2	3
      AT1G01020.1	8
      ```
      - Only genes starting with A and without - in the name are used for aggregation.
   4. Sample Naming Convention
      - Folder names for samples follow the pattern: ```<Genotype>_<Line>_<Replicate>```
      - Example Folders:
      ```aiignore
      KO_L1_R1/
      KO_L1_R2/
      WT_L2_R1/
      WT_L2_R2/
      ```
      - The folder name determines sample grouping for avering and plotting by genotype and line. 
   
   5. Directory Structure Assumptions
      - Example:
      ```aiignore
      ├── data/
      │   └── Thalemine_gene_names.csv  # Annotation CSV
      ├── example_quant/
      │   ├── KO_L1_R1/quant.sf
      │   ├── KO_L1_R2/quant.sf
      │   ├── WT_L2_R1/quant.sf
      │   ├── WT_L2_R2/quant.sf
      │   └── ...
      ```
      - *Assumption*: The dashboard will recursively read each folder under the expression data path for ```quant.sf``` files.
   
## Installation (Docker)

1. Build the Docker image

    ```bash
    docker-compose build
   ```
2. Run the app
   ```bash
    docker-compose up
   ```
This will start the app inside the container
3. Access the app
   - From your hist machine (localhost):
   Open your browser at:
   ```aiignore
    http://127.0.0.1:8050
   ```
   - From another device on the same network:
     1. Find your host's LAN IP address:
     ```aiignore
      ip addr show   # Linux 
      ipconfig       # Windows
     ```
     2. Open on another device:
     ```aiignore
      http://<device-ip>:8050
     ```
4. Data mounting

    The ```./data``` folder in your project is automatically mounted into the container at ```/app/data```.
   - Place your annotation CSV and expression folders there
   - You can replace files in ```./data``` without rebuilding the Docker image


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