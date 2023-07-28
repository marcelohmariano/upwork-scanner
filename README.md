# Upwork Portal Scanner

This is a simple scanner for the [Upwork](https://www.upwork.com/) portal.

## Getting Started

These instructions will guide you on how to set up and run the project on your
local machine.

### Prerequisites

To run this project, you will need the following tools:

* [Python](https://www.python.org/) >= 3.9
* [GNU Make](https://www.gnu.org/software/make/) >= 3.81
* [Docker](https://docs.docker.com/get-docker/) >= 20.10

### Running with Docker

Go to the project root directory and build the docker image:

```shell
make dockerize
```

Start the Selenium server for local testing using `docker compose`:

```sh
make start-selenium-server
```

Run the docker image:

```sh
docker run -it --rm --network upwork-scanner-network \
  -v "$PWD":/scan \
  -e USER=<user> \
  -e PASS=<pass> \
  -e SECRET_ANSWER=<secret_answer> \
  -e SELENIUM_SERVER_URL='http://selenium-server:4444' \
  upwork-scanner
```

You should see an ouput similar to this:

```sh
2023-07-28 14:19:03 INFO: starting scan
2023-07-28 14:19:03 INFO: logging in to the portal
2023-07-28 14:19:14 INFO: extracting job matches
2023-07-28 14:19:34 INFO: extracting user data
2023-07-28 14:19:40 INFO: extracting address data
```

When successful, the scanner will create a `scan.json` file in the current directory.

### Running with Python

Go to the project root directory and create a virtualenv if it's not created:

```sh
make venv
source venv/bin/activate
```

Start the Selenium server:

```sh
make start-selenium-server
```

Run the `upwork` module:

```sh
python -m upwork \
  --user <user> \
  --password <pass> \
  --secret-answer <answer> \
  --selenium-server-url <url> \
  --out-file "scan.json"
```
You should see an ouput similar to this:

```sh
2023-07-28 14:19:03 INFO: starting scan
2023-07-28 14:19:03 INFO: logging in to the portal
2023-07-28 14:19:14 INFO: extracting job matches
2023-07-28 14:19:34 INFO: extracting user data
2023-07-28 14:19:40 INFO: extracting address data
```

When successful, the scanner will create a `scan.json` file in the current directory.

## Testing

This project uses the [selenium/standalone-chrome](https://hub.docker.com/r/selenium/standalone-chrome)
image with Docker Compose to help with the tests. Use the `make test` command to
run them.

## Linting

This project uses [pylint](https://www.pylint.org/) and [mypy](https://mypy-lang.org/)
to check the source code. Use the `make lint` command to run them.
