import requests
import os
from typing import Literal, Any
from pydantic import BaseModel, Field
import tyro
from dotenv import load_dotenv
import stamina
import structlog

load_dotenv()
logger = structlog.get_logger()

class Args(BaseModel):
    query: str = Field(..., description="Search query term, e.g., 'natural language processing'")
    venue: Literal["ACL Anthology"] = Field("ACL Anthology", description="Publication venue to filter papers from")
    num_papers: int = Field(10, gt=0, description="Number of papers to retrieve")
    output_dir: str = Field("acl_papers", description="Directory to save downloaded PDFs")
    api_key: str | None = Field(None, description="Optional API key for Semantic Scholar")
    retry_attempts: int = Field(3, description="Number of retry attempts for downloading PDFs")


def fetch_acl_papers(query: str, max_results: int = 100) -> dict[str, dict[str, Any]]:
    """
    Fetches ACL papers based on a query, using pagination to retrieve more results if available.
    
    Parameters:
    - query (str): The search term to query papers.
    - max_results (int): The maximum number of papers to fetch in total.
    
    Returns:
    - dict[str, dict[str, Any]]: A dictionary with ACL IDs as keys and dictionaries containing
      the title and paperId as values.
    """
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": query,
        "fields": "paperId,title,externalIds,openAccessPdf",
        "limit": 100
    }
    headers = {"x-api-key": api_key} if api_key else {}

    acl_papers = {}
    total_fetched = 0
    token = None

    while total_fetched < max_results:
        if token:
            params["token"] = token

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Process and store ACL papers
            for paper in data.get("data", []):
                external_ids = paper.get("externalIds", {})
                if "ACL" in external_ids:
                    acl_id = external_ids["ACL"]
                    acl_papers[acl_id] = {
                        "title": paper.get("title"),
                        "paperId": paper.get("paperId"),
                        "openAccessPdf": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
                    }
                    total_fetched += 1
                    if total_fetched >= max_results:
                        break

            # Get the next token for pagination, or break if no more pages
            token = data.get("token")
            if not token:
                break

        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            break
    
    logger.info(f"Retrieved {len(acl_papers)} ACL papers.")
    return acl_papers


@stamina.retry(on=requests.exceptions.RequestException, attempts=3)
def download_pdf(pdf_url: str, pdf_filename: str) -> bool:
    """
    Attempts to download a PDF file from the given URL and save it to the specified filename.
    Retries up to 3 times on network-related exceptions.

    Parameters:
    - pdf_url (str): The URL of the PDF to download.
    - pdf_filename (str): The path where the PDF will be saved.

    Returns:
    - bool: True if download is successful, False otherwise.
    """
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()
    
    with open(pdf_filename, "wb") as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)
    
    return True


def get_pdfs_from_acl_id(acl_papers: dict[str, dict[str, Any]], output_dir: str = "acl_papers") -> None:
    """
    Downloads PDFs for the given ACL papers if a PDF URL is available, with retry capability,
    and provides a summary of results.

    Parameters:
    - acl_papers (Dict[str, Dict[str, Any]]): Dictionary of ACL papers with ACL IDs as keys and metadata as values.
    - output_dir (str): Directory to save downloaded PDFs.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Track successful and failed downloads
    fetched_count = 0
    unable_to_fetch = []

    for acl_id, details in acl_papers.items():
        pdf_url = details.get("openAccessPdf")
        
        if pdf_url:
            pdf_filename = os.path.join(output_dir, f"{acl_id}.pdf")
            try:
                success = download_pdf(pdf_url, pdf_filename)
                if success:
                    logger.info(f"Downloaded PDF for {acl_id}: {details['title']}")
                    fetched_count += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download PDF for {acl_id}: {details['title']} after 3 attempts. Error: {e}")
                unable_to_fetch.append(f"{acl_id}: {details['title']}")
        else:
            logger.error(f"No PDF available for {acl_id}: {details['title']}")
            unable_to_fetch.append(f"{acl_id}: {details['title']}")

    logger.info(f"\nSummary:\nFetched {fetched_count} PDFs.\n")
    logger.warning(f"Unable to fetch {len(unable_to_fetch)} PDFs:\n" + "\n".join(unable_to_fetch))


def main(args: Args) -> None:
    """
    Main function to fetch and download ACL papers.
    """
    logger.info(f"Setting up config {args.model_dump()}")
    if args.api_key:
        os.environ["SEMANTIC_SCHOLAR_API_KEY"] = args.api_key

    acl_papers = fetch_acl_papers(query=args.query, max_results=args.num_papers)

    get_pdfs_from_acl_id(acl_papers, output_dir=args.output_dir)


if __name__ == "__main__":
    args = tyro.cli(Args)
    main(args)