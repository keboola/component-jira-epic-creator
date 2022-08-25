Jira Epic Creator
=============

Jira is an issue tracking application.

This application creates an epic with defined issues.

**Table of contents:**

[TOC]

Functionality notes
===================
An input table can be used with the following structure:
"issue_name","issue_description","issue_type"

This will create child issues for the epic.

Prerequisites
=============

Get the API token
using [this guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)


Configuration
=============

##Configuration Schema

- User email (user_email) - [REQ] Email of the user who create the API token
- Api token (#api_token) - [REQ] API token for JIRA cloud
- Project (project) - [REQ] Id of project to create the Epic in
- Server (server) - [REQ] Link to Jira Cloud server, e.g. https://myjira.atlassian.net
- Epic name (epic_name) - [REQ] Name of the epic to be created

Sample Configuration
=============

```json
{
  "parameters": {
    "user_email": "mail@mail.com",
    "#api_token": "SECRET_VALUE",
    "project": "PROJECT_ID",
    "server": "https://myjira.atlassian.net",
    "epic_name": "NEW EPIC CREATED BY COMPONENT"
  },
  "action": "run"
}
```

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in
the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/)