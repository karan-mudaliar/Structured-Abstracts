import requests 
import os  
from typing import Literal 
from pydantic import BaseModel, Field
import tyro

class Config(BaseModel):
    query: str = Field(..., description="Search query term, e.g., 'natural language processing'")
    venue: Literal["ACL Anthology"] = Field("ACL Anthology", description="Publication venue to filter papers from")
    num_papers: int = Field(10, gt=0, description="Number of papers to retrieve")
    output_dir: str = Field("acl_papers", description="Directory to save downloaded PDFs")
    api_key: str = Field(None, description="Optional API key for Semantic Scholar")


