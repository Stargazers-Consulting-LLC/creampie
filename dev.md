# Developing CREAMPIE

## Frontend

- React
- Vite

## API

## Backend

- FastAPI
- SQLAlchemy?
- PostgreSQL

## CLI Stuff

### Setup

1. Install Python

- `sudo apt update && sudo apt -y upgrade`
- `sudo apt -y upgrade python3`
- `sudo apt -y install python3-pip`

2. Install Poetry and dependencies.

- `sudo apt -y install python3-poetry`
- `poetry install --sync`

3. Credentials (TODO)

4. Install Node<sup>[1]</sup>

- `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash`
- `\. "$HOME/.nvm/nvm.sh"`
- `nvm install 22`
- `corepack enable yarn`

## Running the Python App

- Run from root directory with
- - `poetry run fastapi dev cream_api/main.py`

- Adding additional dependencies:
- - `poetry add PACKAGE`
- Development dependencies:
- - `poetry add -D PACKAGE`

## Running javascript app

- CD into working directory
- - `cd creampie_ui`
- Run yarn
- -`yarn dev`

## Next Steps

- Write DB generating script
- Fill a SQLite3 DB with STUFF (Stuff that doesn't require User Access Tokens)
- Get basic page layouts working
- User signup
- User Access Token grants
- Recommentations? 👀👀👀👀

## Required information

## Appendix

[1] [Node docs](https://nodejs.org/en/download)
