# Structured Abstracts

This repository is a demo repo for fetching papers and summerizing them into structured abstracts.

## Installation Guide

### Step 1: Install `uv` by Astral

The tool requires `uv` by Astral for dependency management. Follow the installation instructions for your operating system:

#### Mac/Linux

Run the following command in your terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

run the following command in your terminal:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/karan-mudaliar/Structured-Abstracts.git
cd Structured-Abstracts
```

### Step 3: Install Dependencies

```bash
uv sync
```

### Step 4: Activate the Virtual Environment

#### Mac/Linux

Run the following command in your terminal:

```bash
source .venv/bin/activate
```

#### Windows

run the following command in your terminal:

```bash
.venv\Scripts\Activate
```

### Step 5: Run the Script to get some papers

```bash
python src/get_papers.py --query "embedding | retrieval | natural language processing" --num-papers 500 --output-dir data/papers
```

## Overview of `get_papers.py`

The `get_papers.py` script is a Python script that allows you to search for academic papers using a specified query and save the results to a local directory. This script uses the Semantic Scholar API to fetch paper data based on the provided query.

#### Script Inputs

The script accepts several parameters:

`--query` (required): The search query term, e.g., "natural language processing". You can use logical operators for advanced search, e.g., "embedding | retrieval".
`--venue`: The publication venue to filter papers from. Currently, only "ACL Anthology" is supported.
`--num-papers`: The maximum number of papers to fetch. Default is 10. THIS DOES NOT GUARANTEE THAT YOU WILL GET THIS MANY PAPERS. IT IS JUST THE MAXIMUM NUMBER OF PAPERS THAT CAN BE FETCHED
`--output-dir`: The directory to save downloaded PDFs. Default is "acl_papers".
`--api-key`: Optional API key for Semantic Scholar. It's recommended for higher request limits on the API.
`--retry-attempts`: Number of retry attempts for downloading PDFs in case of network issues. Default is 3.

#### Example Usage
To fetch a maximum 500 papers related to "embedding" or "retrieval" and save them to the data/papers directory, use the following command:

```bash
python src/get_papers.py --query "embedding | retrieval" --num-papers 500 --output-dir data/papers
```


### API Key Configuration

An API key isn't needed, but it's recommended for higher request limits on the Semantic Scholar API. If you have an API key, you can set it as an environment variable in .env file named `SEMANTIC_SCHOLAR_API_KEY`. 
