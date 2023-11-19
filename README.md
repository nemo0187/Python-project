# Python-project
C2C project written in Python
# Command and Control Server

## Overview

This project consists of two Python scripts, `server.py` and `client.py`, implementing a basic command and control (C2) server and agent system. The server manages multiple agents on different ports, allowing remote command execution and file transfer.

## Server (`server.py`)

### Features

- Multithreaded design to handle multiple connections simultaneously.
- Dynamic port allocation for each agent.
- Command handling for executing shell commands on connected agents.
- File upload and download capabilities.

### Usage

1. Run the server using `python3 server.py`.
2. The server will display a welcome message and start listening on predefined ports.
3. Enter `help` to see a list of available commands.
4. Enter `list` to view active agent sessions.
5. Enter the agent's port number to interact with a specific session.
6. Use `exit` to quit the program.

## Client (`client.py`)

### Features

- Connects to the server with a specified IP address.
- Executes commands received from the server.
- Handles file upload and download.

### Usage

Run the client using `python3 client.py -ip <server_ip>`.

- `<server_ip>`: IP address of the command and control server.

### Commands

- `cd <directory>`: Change the current working directory on the agent.
- `download <filename>`: Download a file from the agent.
- `upload <filename>`: Upload a file to the agent.
- `exit`: Terminate the agent session.

## Dependencies

- Python 3.x
- Required Python modules: `socket`, `threading`, `time`, `sys`, `queue`, `os`, `pyfiglet`, `subprocess`, `random`, `argparse`.

## Disclaimer

This project is for educational purposes only. Misuse of this software for malicious intent is strictly prohibited.
