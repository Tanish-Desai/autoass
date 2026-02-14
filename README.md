# SQL Assignment Generator

**SQL Assignment Generator** is a Python-based tool designed to automate the creation of database assignment reports for students. It connects to an Oracle Database, executes a predefined set of SQL queries (setup and assignment tasks), captures the output, and generates a formatted Markdown report with embedded "terminal-style" screenshots of the results.

This tool is particularly useful for generating clean, consistent lab reports for DBMS courses (e.g., BCSE302P).

## 🚀 Features

-   **Automated Query Execution**: Reads setup and assignment queries from a JSON configuration file.
-   **Oracle Database Integration**: Supports both "Thin" (Network) and "Thick" (Direct) connections to Oracle (XE/Enterprise).
-   **Smart Connection Handling**: Automatically attempts to find Oracle Client libraries if standard network connection fails.
-   **Markdown Report Generation**: clear, formatted Markdown output ready for PDF export (via VS Code or Obsidian).
-   **Visual Output generation**: Renders query results as "terminal screenshots" (images) to simulate real execution environments.
-   **Auto-Cleanup**: automatically cleans up (DROPS) temporary tables created during the session.

## 🛠️ Prerequisites

Before running the script, ensure you have the following installed:

1.  **Python 3.x**
2.  **Oracle Database** (Express Edition or Enterprise)
3.  **Oracle Instant Client** (if using Thick mode/Direct connection)

## 📦 Installation

1.  Clone this repository or download the source code.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: The project relies on `oracledb`, `pandas`, and `Pillow`.*

## ⚙️ Configuration

### 1. Database Configuration
Open `automatic_ass.py` and update the `DB_CONFIG` dictionary with your Oracle Database credentials:

```python
DB_CONFIG = {
    "user": "system",          # Your Oracle username
    "password": "YOUR_PASSWORD", # <--- CHANGE THIS
    "service_name": "xe",      # 'xe' for Express Edition or 'orcl'
    "host": "localhost",
    "port": 1521
}
```

### 2. User Details
When you run the script, it will interactively ask for your details (Name, Reg No, Lab Title, etc.).
To skip this interactive prompt and use hardcoded defaults every time:
1.  Open `automatic_ass.py`.
2.  Update the `USER_CONFIG` dictionary with your details.
3.  When running the script, enter `0` at the first prompt.

```python
USER_CONFIG = {
    "regno" : "YOUR_REG_NO",
    "name" : "Your Name",
    "labNo" : "1",
    "labTitle" : "Assignment Title",
    "faculty" : "Faculty Name",
    "slot" : "L00-L00"
}
```

### 3. Define Queries
Edit `queries.json` to define your assignment tasks. The file structure is:

```json
{
  "setup_queries": [
    {
      "q": "Description of setup task",
      "sql": "CREATE TABLE ..."
    }
  ],
  "assignments": [
    {
      "q": "Question text",
      "sql": "SELECT * FROM ..."
    }
  ]
}
```

## ▶️ Usage

Run the main script:

```bash
python automatic_ass.py
```

### Results
1.  The script will execute all queries defined in `queries.json`.
2.  Images of the results will be saved in the `assignment_images/` directory.
3.  A final report **`DBMS_Assignment.md`** will be generated in the root directory.

### Exporting to PDF
Open `DBMS_Assignment.md` in **VS Code** (using `Markdown PDF` extension) or **Obsidian** and export it to PDF to submit your assignment.

## 📂 Project Structure

- `automatic_ass.py`: Main script for database connection and report generation.
- `queries.json`: Configuration file containing SQL queries.
- `requirements.txt`: List of Python dependencies.
- `assignment_images/`: Directory where generated screenshots are stored.
- `DBMS_Assignment.md`: The generated output report.

## ⚠️ Notes

-   **Table Cleanup**: The script attempts to drop all tables created during the session (detected via `CREATE TABLE` commands) to keep your database clean.

## ❓ Troubleshooting

### Connection Issues
If you see errors related to `DP-1010`, `10061` (Connection Refused), or `12541` (No Listener):
1.  **Check Oracle Service**: Ensure your Oracle Database service (e.g., OracleServiceXE) and TNS Listener are running in Windows Services.
2.  **Verify DB Config**: Double-check the `host`, `port` (default 1521), and `service_name` in `DB_CONFIG`.
3.  **Thick Mode**: The script automatically attempts "Thick Mode" (using local Oracle Client libraries) if the network connection fails. Ensure you have the Oracle Instant Client or a full Oracle installation, and that its `bin` directory is in your system PATH or one of the standard locations checked by the script.
