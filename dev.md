# Frontend

React, Vite and Typescript

# API

# Backend

- FastAPI
- sqlite3
- ORM?

# CLI Stuff

## Setup

Create symlink from home to your code folder

- `ln -s YOUR/PATH/HERE ~code`
- Note that your path probably starts with `/mnt/c/` on windows.
  CD into code folder
- `cd ~code/stream`
  Initialize Project

1. Install Python

- `sudo apt update && sudo apt upgrade`
- `sudo apt -y upgrade python3`
- `sudo apt -y install python3-pip`
- `sudo apt -y install python3-pip`

2. Initialize venv

- `python3 -m venv .venv`
- `source .venv/bin/activate`

3. Install Poetry and dependencies.

- `sudo apt -y install python3-poetry`
- `poetry install`

4. Credentials (Fix this)
5. Install Node<sup>[1]</sup>

- `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash`
- `\. "$HOME/.nvm/nvm.sh"`
- `nvm install 22`
- `corepack enable yarn`

## Running the Python App

- Activate Python venv (via Ubuntu)
- - `cd ~code/stream`
- - `source .venv/bin/activate`
- Run from root directory with
- - `fastapi dev api/main.py`
- Leave the Python venv
- - `deactivate`

## Running javascript app

- CD into working directory
- - `cd ~code/stream/frontend`
- Run yarn
- -`yarn dev`

Adding additional dependencies:
`poetry add PACKAGE`

# Next Steps

- Write DB generating script
- Fill a SQLite3 DB with STUFF (Stuff that doesn't require User Access Tokens)
- Get basic page layouts working
- User signup
- User Access Token grants
- Recommentations? 👀👀👀👀

# Required information:

## Twitch

### App Access Token

- [Get Users](https://dev.twitch.tv/docs/api/reference/#get-users)
- [Get Channel Information](https://dev.twitch.tv/docs/api/reference/#get-channel-information)
- [Get Games](https://dev.twitch.tv/docs/api/reference/#get-games)
- [Get Top Games](https://dev.twitch.tv/docs/api/reference/#get-top-games)

### User Access Token

- [Get Followed Channels](https://dev.twitch.tv/docs/api/reference/#get-followed-channels)
- [Get Channel Followers](https://dev.twitch.tv/docs/api/reference/#get-channel-followers)

## Twitch Authentication

- Getting Access Tokens
- - https://dev.twitch.tv/docs/authentication/#user-access-tokens
- - https://dev.twitch.tv/docs/authentication/#app-access-tokens

- Auth Grant Flow
- - https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#authorization-code-grant-flow

[1] https://nodejs.org/en/download
