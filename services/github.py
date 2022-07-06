import github
from pydantic import BaseModel


class GithubSettings(BaseModel):
    token: str

    repo: str
    workflow_file: str
    ref: str


class Settings(BaseModel):
    settings: GithubSettings

    class Config:
        env_prefix = "GITHUB_"


class Github:
    client: github.Github
    token: str

    repo_name: str
    workflow_file: str
    ref: str

    def __init__(self, *, settings: Settings):
        github_settings = settings.settings

        self.repo_name = github_settings.repo
        self.workflow_name = github_settings.workflow_file
        self.ref = github_settings.ref

        token = github_settings.token
        self.client = github.Github(login_or_token=token)

    def dispatch_workflow(self) -> bool:
        repo = self.client.get_repo(full_name_or_id=self.repo_name)
        workflow = repo.get_workflow(id_or_name=self.workflow_file)

        return workflow.create_dispatch(self.ref)

    def infrastructure_update(self):
        return self.dispatch_workflow()
