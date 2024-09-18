import logging

from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import Issue

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

KEY_DESCRIPTION = 'epic_description'
KEY_ORIGINAL_EPIC = 'original_epic_key'

KEY_API_TOKEN = '#api_token'
KEY_PROJECT = 'project'
KEY_SERVER = "server"
KEY_USER_EMAIL = "user_email"
KEY_EPIC_NAME = "epic_name"

REQUIRED_PARAMETERS = [KEY_API_TOKEN, KEY_PROJECT, KEY_SERVER, KEY_USER_EMAIL, KEY_EPIC_NAME, KEY_ORIGINAL_EPIC]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    def run(self):
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters

        server = params.get(KEY_SERVER)
        user_email = params.get(KEY_USER_EMAIL)
        api_token = params.get(KEY_API_TOKEN)
        jira_project = params.get(KEY_PROJECT)
        epic_name = params.get(KEY_EPIC_NAME)
        original_epic_key = params.get(KEY_ORIGINAL_EPIC)

        jira_client = self.init_jira_client(server, user_email, api_token)
        logging.info(f"Copying epic {original_epic_key} to create new epic {epic_name}")

        original_epic = jira_client.issue(original_epic_key)
        new_epic = self.copy_epic(jira_client, jira_project, epic_name, original_epic)
        logging.info(f"New epic created with key: {new_epic.key}")

        self.copy_child_issues(jira_client, jira_project, original_epic, new_epic)
        logging.info(f"Child issues copied from {original_epic_key} to {new_epic.key}")

    @staticmethod
    def init_jira_client(server: str, user_email: str, api_token: str) -> JIRA:
        try:
            jira_options = {'server': server, 'rest_api_version': '3'}
            return JIRA(options=jira_options, basic_auth=(user_email, api_token))
        except JIRAError as jira_exc:
            raise UserException("Failed to authenticate client, please revalidate your email and token.") from jira_exc

    @staticmethod
    def copy_epic(jira_client: JIRA, jira_project: str, epic_name: str, original_epic: Issue) -> Issue:
        issue_raw = original_epic.raw
        description = issue_raw.get('fields', {}).get('description', None)

        try:
            fields = {
                'project': {'key': jira_project},
                'summary': epic_name,
                'description': description,
                'issuetype': {'name': 'Epic'},
            }
            logging.info(f"Creating new epic with fields: {fields}")
            new_epic = jira_client.create_issue(fields=fields)
            return new_epic
        except JIRAError as jira_exc:
            logging.error(f"Error response: {jira_exc.response.text}")
            raise UserException(
                "Failed to create new epic, validate that the jira project name and epic name are valid") from jira_exc

    @staticmethod
    def copy_child_issues(jira_client: JIRA, jira_project, original_epic: Issue, new_epic: Issue):
        jql_query = f'"issueLink" = {original_epic.key}'
        child_issues = jira_client.search_issues(jql_query)
        logging.info(f"Found {len(child_issues)} child issues to copy")

        for issue in child_issues:
            issue_raw = issue.raw
            fields = {
                'project': {'key': jira_project},
                'summary': issue_raw.get('fields', {}).get('summary'),
                'description': issue_raw.get('fields', {}).get('description'),
                'issuetype': {'name': issue.fields.issuetype.name},
                'parent': {'key': new_epic.key},
            }
            logging.info(f"Creating child issue with fields: {fields}")
            try:
                jira_client.create_issue(fields=fields)
            except JIRAError as jira_exc:
                logging.error(f"Error response: {jira_exc.response.text}")
                raise UserException(
                    f"Failed to create child issue for {issue.key}, validate that the fields are correct") from jira_exc


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
