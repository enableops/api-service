import json
from typing import Dict, List

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class GoogleUserAPI:
    credentials: str

    def __init__(self, *, credentials: str):
        self.credentials = credentials

    def get_profile(self) -> Dict[str, str]:
        credentials = Credentials.from_authorized_user_info(
            info=json.loads(self.credentials)
        )

        with build("oauth2", "v2", credentials=credentials) as service:
            user_info: Dict[str, str] = service.userinfo().get().execute()

        self.credentials = credentials.to_json()

        return user_info

    def get_project_ids(self) -> List[Dict[str, str]]:
        credentials = Credentials.from_authorized_user_info(
            info=json.loads(self.credentials)
        )

        with build(
            "cloudresourcemanager", "v1", credentials=credentials
        ) as service:
            filter = "lifecycleState:ACTIVE"
            projects_response = service.projects().list(filter=filter).execute()

            projects = [
                {"name": project["name"], "id": project["projectId"]}
                for project in projects_response["projects"]
            ]

        self.credentials = credentials.to_json()

        return projects
