# SimplDB

SimplDB is a SQL-based relational database management system (DBMS) built using Python.

SimplDB leverages [PLY](https://ply.readthedocs.io/en/latest/index.html) for lexing and parsing SQL statements.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` package manager

### Environment Setup

1. **Clone the Repository**

   ```bash
   git clone 
   cd simpldb
   ```

2. **Create a virtual environment**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Interacting with the DBMS
1. **Run the DB server**

    ```bash
    cd src
    uvicorn server:app --reload
    ```

2. **Run the SQL client**

    ```bash
    python src/client.py
    ```

### Running Tests
1. **Run PyTest**

    ```bash
    pytest
    ```