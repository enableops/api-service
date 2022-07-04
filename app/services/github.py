from github import Github

from app.core.config import settings


class GithubAPI:
    client: Github

    def __init__(self, token: str = settings.GITHUB.TOKEN):
        self.client = Github(login_or_token=token)

    def dispatch_workflow(
        self,
        repo_name: str,
        workflow_file: str,
        ref: str,
    ) -> bool:

        repo = self.client.get_repo(full_name_or_id=repo_name)
        workflow = repo.get_workflow(id_or_name=workflow_file)

        return workflow.create_dispatch(ref)


def dispatch_apply_workflow() -> bool:
    gh = GithubAPI()

    return gh.dispatch_workflow(
        repo_name=settings.GITHUB.WORKFLOW_REPO,
        workflow_file=settings.GITHUB.WORKFLOW_TERRAFORM,
        ref=settings.GITHUB.WORKFLOW_REF,
    )
