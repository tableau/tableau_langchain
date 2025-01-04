
from typing import TypedDict, Annotated, Sequence, Dict, Optional

from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep


class TableauCredentials(BaseModel):
    """
    Tableau credentials for authenticating via HTTP into any Tableau analytics environment (or site)
    that a user has access to. This allows the model to act on behalf of the user, inheriting the
    permissions and priviledges assigned to the particular user for actions such as querying data
    """
    session: str = Field(..., description="Contains the response from a succesful REST API authentication call to Tableau. The session is valid for 2 hours by default.")
    url: str = Field(..., description="URL or domain to the Tableau site (Cloud or Server)")
    site: str = Field(..., description="Site name or 'contentURL' used to identify the Tableau environment")


class TableauDatasource(BaseModel):
    """
    Metadata for a specific Tableau datasource tracked via the Agent state so that it can carry multiple
    conversations about the same datasource and target it for tool calls such as querying. This class and
    all its inputs should be optional to account for scenarios when client apps or the user do not know beforehand
    which datasource is relevant to their needs or on the otherhand account for when the client app does know
    the context such as when a user is interacting visually with datasources on the browser
    """
    luid: str = Field(None, description="Unique identifier of a datasource, used to perform VDS queries")
    name: str = Field(None, description="A user friendly name for the datasource")
    description: str = Field(None, description="A description used to help Agents understand the purpose and use of the datasource")

# define custom state for the cra agent
class TableauAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    is_last_step: IsLastStep # required to customize create_react_agent
    tableau_credentials: TableauCredentials
    datasource: Optional[TableauDatasource]
