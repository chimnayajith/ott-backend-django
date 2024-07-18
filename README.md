# ott-backend-django

Welcome to the Backend of OTT Project.

## Setup Instructions

### 1. Creating a Virtual Environment

Navigate to the root of the repository and execute the following command:

```bash
python3 -m venv .venv
```

This command creates a virtual environment named `.venv` in the current directory.

### 2. Activating the Virtual Environment

Execute the following command to activate the virtual environment:

```bash
source .venv/bin/activate
```

### 3. Installing Requirements

Run the following command to install all the dependencies listed in the requirements.txt file. Ensure that your virtual environment is activated before executing this command.

```bash
pip3 install -r requirements.txt
```

### 4. Running Migrations

Execute the following command to apply any pending migrations to the database:

```bash
python3 manage.py migrate
```

### 5. Starting the Development Server

To start the Django development server, run the following command:

```bash
python3 manage.py runserver
```
