from pydantic import BaseModel


class GithubConfig(BaseModel):
    """Stores github-related settings"""

    TOKEN: str
    WORKFLOW_REPO: str
    WORKFLOW_REF: str
    WORKFLOW_CUSTOMERS: str
    WORKFLOW_TERRAFORM: str
