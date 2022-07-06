from typing import Dict, List

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from services import googleauth as ga

class GoogleUserAPI:
    credentials: Credentials

    @classmethod
    def from_user_info

    def __init__(self, *, credentials: Credentials):
        self.credentials = Credentials



    def get_profile(self) -> Dict[str, str]:
        with build("oauth2", "v2", credentials=self.credentials) as service:
            return service.userinfo().get().execute()

    def get_project_ids(self) -> List[Dict[str, str]]:
        with build(
            "cloudresourcemanager", "v1", credentials=self.credentials
        ) as service:
            filter = "lifecycleState:ACTIVE"
            projects_response = (
                service.projects().list(filter=filter).execute()
            )

            projects = [
                {"name": project["name"], "id": project["projectId"]}
                for project in projects_response["projects"]
            ]

            return projects

def get_gapi():
    return GoogleUserAPI()
