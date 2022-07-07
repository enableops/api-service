import os

import github
from pydantic import BaseModel, BaseSettings


class GithubSettings(BaseModel):
    token: str

    repo_name: str
    workflow_file: str
    ref: str


class Settings(BaseSettings):
    github: GithubSettings

    class Config:
        env_nested_delimiter = "__"
        secrets_dir = os.getenv("SECRETS_PATH")


class Github:
    client: github.Github
    token: str

    repo_name: str
    workflow_file: str
    ref: str

    def __init__(self, *, settings: Settings):
        github_settings = settings.github

        self.repo_name = github_settings.repo_name
        self.workflow_file = github_settings.workflow_file
        self.ref = github_settings.ref

        token = github_settings.token
        self.client = github.Github(login_or_token=token)

    def dispatch_workflow(self) -> bool:
        repo = self.client.get_repo(full_name_or_id=self.repo_name)
        workflow = repo.get_workflow(id_or_name=self.workflow_file)
        dispatch = workflow.create_dispatch(ref=self.ref)
        return dispatch

    def request_update(self) -> bool:
        return self.dispatch_workflow()


def get_github() -> Github:
    settings = Settings()
    return Github(settings=settings)
