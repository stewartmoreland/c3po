# C3PO

Human Cyborg Relations... Also just another Slack bot.

## Local Development

### Required software

- [Docker](https://www.docker.com/get-started)
- Python 3.9
  - [macOS Using Homebrew](https://formulae.brew.sh/formula/python@3.9)
  - [Windows Using Chocolatey](https://community.chocolatey.org/packages/python/3.9.0)
  - [Download](https://www.python.org/downloads/)
- [Pipenv](https://realpython.com/pipenv-guide/#pipenv-introduction)

### Running the app locally

This app uses Docker for local development. To start the application, you'll need a `secrets.env` file stored under the working app directory. That file should look something like the sample file below.

```shell
# This value is required and can be anything. It is
# used for signing the session.
FLASK_SECRET_KEY=changeme

# Set environment to 'LOCAL' to use LocalConfig in conf
ENVIRONMENT=LOCAL

# Slack OAuth token and signing secret for API access and
# request validation
SLACK_TOKEN=xoxb-1234567-0987654321-AbCdefG1234567hIJklmn0
SLACK_SIGNING_SECRET=abcdefg1234567
```

Once the `secret.env` file has been created, start the app using Docker compose.

```shell
docker compose up --build
```

### Installing packages in a virtual environment

Use the command below to install the app and all of its dependencies from the project root directory.

```shell
pipenv install -e .
```

If you haven't run `pipenv` from this directory previously, it will create a new virtual environment and install all of the packages & dependencies to that virtual environment.

To activate the new virtual environment, use `pipenv shell`.

If using a language server in your IDE, make sure the interpreter is set to the virtual environment created by pipenv.
