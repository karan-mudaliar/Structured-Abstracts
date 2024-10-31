import requests
import os
import random
from pydantic import BaseModel, Field
import tyro


class DownloadPapersConfig(BaseModel):
    num_papers: int = Field(100, description="Number of papers to download", ge=1)
    output_dir: str = Field("acl_papers", description="Directory to save downloaded papers")
    random_seed: int = Field(42, description="Seed for reproducibility")


def ensure_output_dir_exists(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

BULK_URL = "https://aclanthology.org/anthology.json"


def download_papers(num_papers: int, output_dir: str, random_seed: int) -> None:
    """
    Downloads a specified number of randomly selected ACL papers as PDFs.

    Parameters:
        num_papers (int): Number of papers to download.
        output_dir (str): Directory where PDFs are saved.
        random_seed (int): Random seed for reproducibility.
    """
    # Fetch the bulk JSON file
    response = requests.get(BULK_URL)
    response.raise_for_status()
    
    papers = response.json()

    # Filter to only ACL papers (based on ID prefix like 'P', 'J' used by ACL)
    acl_papers = [
        (paper_id, info) for paper_id, info in papers.items()
        if paper_id.startswith(('P', 'J')) and 'pdf_url' not in info
    ]

    # Sort by citation count in descending order if citation count is available
    acl_papers = sorted(acl_papers, key=lambda x: x[1].get('citations', 0), reverse=True)

    # Seed for reproducibility and shuffle the sorted list
    random.seed(random_seed)
    random.shuffle(acl_papers)

    # Ensure the output directory exists
    ensure_output_dir_exists(output_dir)

    # Download selected papers
    paper_count = 0
    for paper_id, paper_info in acl_papers[:num_papers]:
        title = paper_info.get('title', f"paper_{paper_id}")
        pdf_url = f"https://aclanthology.org/{paper_id}.pdf"  # ACL-specific URL format
        sanitized_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
        pdf_filename = os.path.join(output_dir, f"{sanitized_title}.pdf")

        try:
            # Download PDF
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()
            
            # Save PDF
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)
            
            print(f"Downloaded: {title}")
            paper_count += 1

        except Exception as e:
            print(f"Failed to download {title}: {e}")
    
    print(f"Downloaded {paper_count} papers.")

if __name__ == "__main__":
    config = tyro.cli(DownloadPapersConfig)
    download_papers(config.num_papers, config.output_dir, config.random_seed)
