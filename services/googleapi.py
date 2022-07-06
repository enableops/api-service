from typing import Dict, List

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from services import googleauth as ga

class GoogleUserAPI:
    credentials: Credentials

    @classmethod
    def from_user(cls, user: ga.GoogleOAuthUser) -> "GoogleUserAPI":
        info = ga.get_gauth().get_user_credentials_info(user=user)

        return GoogleUserAPI(
            client_id=info["client_id"],
            client_secret=info["client_secret"],
            user=user,
        )

    def get_profile(self) -> Dict[str, str]:
        credentials = self.get_user_credentials(user=self.user)

        with build("oauth2", "v2", credentials=credentials) as service:
            return service.userinfo().get().execute()

    def get_project_ids(self) -> List[Dict[str, str]]:
        credentials = self.get_user_credentials(user=self.user)

        with build(
            "cloudresourcemanager", "v1", credentials=credentials
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

    class Config:

def get_gapi():
    return GoogleUserAPI()
