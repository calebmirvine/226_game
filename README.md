# ICS 226 Game Project

This project is a multiplayer treasure hunt game developed for **ICS 226 - Network Programming** at Camosun College.

## Project Evolution

The project originated as a board game focused on exploring **threading** concepts in Python. It has since evolved into a modern web and native application, transitioning to **asyncio** to handle concurrent operations and network communication efficiently.

It is now built using **Django** for the backend and web interface, and utilizes **Briefcase/Toga** for cross-platform native application support (iOS, Android, macOS, Windows, Linux).

## Features

*   **Multiplayer Gameplay**: Supports 2 players competing to find treasures on a grid.
*   **Web Interface**: Responsive web-based game board.
*   **Native App Support**: Can be packaged as a native app using BeeWare's Briefcase.
*   **REST API**: Exposes game state and actions via a RESTful API.
*   **CI/CD**: Automated testing and linting via GitHub Actions.

## Technologies

*   **Python 3.12**
*   **Django 5.1**
*   **Django REST Framework**
*   **BeeWare (Toga & Briefcase)**
*   **Pytest** (Testing)
*   **Pipenv** (Dependency Management)

## Setup and Installation

### Prerequisites

*   Python 3.12+
*   Pipenv (`pip install pipenv`)

### Quick Setup

You can use the provided build script to automate the installation of dependencies and database setup:

```bash
chmod +x build.sh
./build.sh
```

### Manual Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ICS25-004/226_game.git
    cd 226_game
    ```

2.  Install dependencies:
    ```bash
    pipenv install --dev
    ```

3.  Apply database migrations:
    ```bash
    pipenv run website/manage.py migrate
    ```

### Running the Web Application

To start the Django development server:

```bash
pipenv run website/manage.py runserver
```

Access the game at `http://127.0.0.1:8000/`.

### Running Tests

To run the test suite using Pytest:

```bash
pipenv run pytest
```

### Building Native Apps

To build and run the native application (e.g., for macOS or iOS):

```bash
# Update the app code
briefcase update

# Run the app
briefcase run

# Build the app package
briefcase build
```

*Note: Ensure you are in the root directory containing `pyproject.toml` when running Briefcase commands.*

## Project Structure

*   `website/`: Contains the Django project and `game` app.
*   `website/game/`: Main game logic, models, views, and templates.
*   `website/game/tests/`: Test suite split into board, gameplay, and model tests.
*   `pyproject.toml`: Configuration for Briefcase and project metadata.
*   `Pipfile` & `Pipfile.lock`: Dependency definitions.

## Future Plans

*   **WebSockets**: Implement real-time game state updates using Django Channels or similar technology to replace polling.
*   **Mobile-Friendly Interface**: Enhance the Toga native application GUI to be more responsive and touch-friendly for mobile devices.
