import csv
import logging
from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import Issue
from typing import Generator, Optional

from keboola.component.dao import TableDefinition
from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

KEY_API_TOKEN = '#api_token'
KEY_PROJECT = 'project'
KEY_SERVER = "server"
KEY_USER_EMAIL = "user_email"
KEY_EPIC_NAME = "epic_name"

REQUIRED_PARAMETERS = [KEY_API_TOKEN, KEY_PROJECT, KEY_SERVER, KEY_USER_EMAIL, KEY_EPIC_NAME]
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

        issues_file = self.get_single_input_table()

        jira_client = self.init_jira_client(server, user_email, api_token)
        logging.info(f"Creating epic {epic_name}")
        new_epic = self.create_new_epic(jira_client, jira_project, epic_name)
        if issues_file:
            self.create_epic_issues(jira_client, jira_project, new_epic, issues_file)

    def get_single_input_table(self) -> Optional[TableDefinition]:
        input_files = self.get_input_tables_definitions()
        if len(input_files) == 0:
            return None
        if len(input_files) != 1:
            raise UserException("Have 1 and only 1 input table in the input mapping")
        return input_files[0]

    @staticmethod
    def get_issue_definitions_from_table(issues_file: TableDefinition) -> Generator:
        with open(issues_file.full_path, 'r') as in_file:
            yield from csv.DictReader(in_file)

    @staticmethod
    def init_jira_client(server: str, user_email: str, api_token: str) -> JIRA:
        try:
            jira_options = {'server': server}
            return JIRA(options=jira_options, basic_auth=(user_email, api_token))
        except JIRAError as jira_exc:
            raise UserException("Failed to authenticate client, please revalidate your email and token") from jira_exc

    @staticmethod
    def create_new_epic(jira_client: JIRA, jira_project: str, epic_name: str) -> Issue:
        try:
            return jira_client.create_issue(project=jira_project,
                                            customfield_10011=epic_name,
                                            summary=epic_name,
                                            issuetype={'name': 'Epic'})
        except JIRAError as jira_exc:
            raise UserException(
                "Failed to create new epic, validate that the jira project name and epic name are valid") from jira_exc

    def create_epic_issues(self, jira_client: JIRA, jira_project: str, epic: Issue,
                           issues_file: TableDefinition) -> None:
        for issue in self.get_issue_definitions_from_table(issues_file):
            logging.info(f"Creating issue {issue.get('issue_name')}")
            try:
                jira_client.create_issue(project=jira_project,
                                         customfield_10014=epic.key,
                                         summary=issue.get("issue_name"),
                                         description=issue.get("issue_description"),
                                         issuetype=issue.get("issue_type"))
            except JIRAError as jira_exc:
                raise UserException("Failed to create epic issue") from jira_exc


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
