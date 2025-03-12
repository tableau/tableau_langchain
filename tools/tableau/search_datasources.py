from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Dict, Tuple

class SearchInput(BaseModel):
    api_key: str = Field(description="API key for authentication to Tableau Headless BI")
    #datasource_id: str = Field(description="ID of the Tableau datasource")
    metadata: Dict[str, Any] = Field(description="Metadata describing the dataset for accurate querying")
    #endpoint: str = Field(description="Headless BI API endpoint for querying the datasource")
    query: str = Field(description="Search query to find relevent a dataset or data visualisation")

class SearchTableauDatasources(BaseTool):
    print('hey')