import oracledb
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import glob
import sys
import platform
import warnings
import json
import datetime

# Suppress pandas UserWarning about raw DB connections
warnings.filterwarnings('ignore', message='.*pandas only supports SQLAlchemy connectable.*')

# ==========================================
#              CONFIGURATION
# ==========================================
DB_CONFIG = {
    "user": "system",          # Usually 'system' or 'sys'
    "password": "Metsu#$1234", # <--- CHANGE THIS
    "service_name": "xe",      # Usually 'xe' for Express Edition or 'orcl'
    "host": "localhost",
    "port": 1521
}

USER_CONFIG = {
    "regno" : "YYBBBXXXX",
    "name" : "Superman",
    "labNo" : "0",
    "labTitle" : "Practice Exercise",
    "faculty" : "facc",
    "slot" : "L00-L00"
}

def load_queries_from_json(filename="queries.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            return data.get("assignments", []), data.get("setup_queries", [])
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return [], []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {filename}.")
        return [], []

ASSIGNMENTS, SETUP_QUERIES = load_queries_from_json()

# ==========================================
#        PART 1: SMART CONNECTION
# ==========================================
def find_oracle_home():
    """
    Searches common Windows paths for the Oracle Client libraries (oci.dll).
    Used only if the standard network connection fails.
    """
    print("   > Searching for Oracle Home directory...")
    
    # Common paths for Oracle XE and Enterprise on Windows
    search_patterns = [
        r"C:\app\*\product\*\dbhomeXE\bin",
        r"C:\oraclexe\app\oracle\product\*\server\bin",
        r"C:\app\*\product\*\client_*\bin",
        r"C:\app\*\product\*\dbhome_*\bin"
    ]
    
    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            # Return the first valid bin directory found
            return matches[0]
            
    return None

def get_db_connection():
    """
    Tries to connect via Network (Thin mode). 
    If that fails due to Listener errors, switches to Direct (Thick mode).
    """
    user = DB_CONFIG["user"]
    pwd = DB_CONFIG["password"]
    dsn_str = f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['service_name']}"

    # Attempt 1: Standard Network Connection (Thin Mode)
    try:
        print(f"[*] Attempting network connection to {dsn_str}...")
        conn = oracledb.connect(user=user, password=pwd, dsn=dsn_str)
        print("    [+] Success! Connected via Network.")
        return conn
    except oracledb.Error as e:
        error_msg = str(e)
        # Check for specific "Listener Refused" or "Connection Failed" errors
        if "DP-1010" in error_msg or "10061" in error_msg or "12541" in error_msg:
            print(f"    [-] Network failed (Listener issue). Attempting Direct Connection...")
        else:
            # If it's a password error (ORA-01017), don't try the other method.
            print(f"    [!] Connection failed: {error_msg}")
            raise e

    # Attempt 2: Direct "Thick" Connection (Bypasses Listener)
    oracle_bin = find_oracle_home()
    if not oracle_bin:
        raise Exception("Could not find Oracle installation directory automatically. Please fix Listener or add path manually.")

    print(f"    [+] Found Oracle Binaries at: {oracle_bin}")
    
    try:
        # Initialize the C libraries
        oracledb.init_oracle_client(lib_dir=oracle_bin)
        
        # Connect using the local driver (Bequeath connection)
        # Note: We do NOT pass 'dsn' here, relying on local OS auth or SID
        os.environ["ORACLE_SID"] = DB_CONFIG["service_name"]
        
        conn = oracledb.connect(user=user, password=pwd)
        print("    [+] Success! Connected via Direct Driver (Thick Mode).")
        return conn
    except Exception as e:
        print(f"    [!] Direct connection also failed: {e}")
        raise e

# ==========================================
#        PART 2: FAKE SCREENSHOT GEN
# ==========================================
def create_terminal_screenshot(query, result_text, filename):
    """
    Renders text onto a black image using a monospace font.
    """
    # 1. Setup Canvas
    bg_color = (12, 12, 12)  # VS Code Terminal Black
    text_color = (204, 204, 204) # Light Gray
    cmd_color = (255, 255, 255) # White for the command
    prompt_color = (0, 255, 0) # Green for "SQL>" prompt
    
    font_size = 15
    padding = 30
    
    # 2. Load Font (Try Consolas for Windows, else default)
    try:
        if platform.system() == "Windows":
            font = ImageFont.truetype("consola.ttf", font_size)
        elif platform.system() == "Darwin": # Mac
            font = ImageFont.truetype("Menlo.ttc", font_size) 
        else:
            font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    except:
        # Fallback if system fonts aren't found
        font = ImageFont.load_default()

    # 3. Construct Text
    
    # Wrap long lines (The new logic)
    wrapped_query = _wrap_text(query, max_chars=95)
    wrapped_result = _wrap_text(result_text, max_chars=95)
    
    # We pretend we are in SQL Plus or VS Code
    header = f"SQL> {wrapped_query}\n"
    body = f"\n{wrapped_result}\n"
    footer = "\nSQL> _"
    
    full_text = header + body + footer

    # 4. Measure Text to size the image
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    
    bbox = draw.textbbox((0, 0), full_text, font=font)
    text_width = bbox[2]
    text_height = bbox[3]
    
    width = text_width + (padding * 2)
    height = text_height + (padding * 2)

    # 5. Draw the actual image
    img = Image.new('RGB', (width, height), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Draw logic is slightly complex to handle colors, 
    # but for simplicity, we just draw standard text:
    d.text((padding, padding), full_text, font=font, fill=text_color)
    
    img.save(filename)
    return filename

# ==========================================
#        PART 3: MAIN EXECUTION
# ==========================================

def set_user_config():
    print("-----Enter your document details-----")
    print("*** Enter 0 to use default values ***")
    regno = input("Registration No. : ")
    if regno == "0":
        return
    
    USER_CONFIG["regno"] = regno
    USER_CONFIG["name"] = input("Name : ")
    USER_CONFIG["faculty"] = input("Faculty Name : ")
    USER_CONFIG["slot"] = input("Slot : ")
    USER_CONFIG["labNo"] = input("Lab No. : ")
    USER_CONFIG["labTitle"] = input("Lab Title : ")

def execute_sql_safely(conn, sql, task_context=None):
    # --- FIX START: Handle multiple statements separated by semicolons ---
    # If the SQL contains multiple statements (like the bulk INSERTs), split them.
    if ";" in sql and "BEGIN" not in sql.upper(): # Ignore PL/SQL blocks which use semicolons correctly
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        if len(statements) > 1:
            full_result = ""
            for single_stmt in statements:
                # Recursively call this function for each single statement
                # This ensures each INSERT gets executed and counted
                res = execute_sql_safely(conn, single_stmt, task_context) 
                full_result += res + "\n"
            return full_result.strip()
    # --- FIX END ---

    clean_sql = sql.strip().upper()
    
    # 1. Enable DBMS_OUTPUT (Standard PL/SQL printing)
    # This tells the server "buffer any print messages, I will ask for them later"
    cursor = conn.cursor()
    cursor.callproc("dbms_output.enable")
    
    result_text = ""
    
    try:
        # A. SELECT / WITH -> Use Pandas
        if clean_sql.startswith("SELECT") or clean_sql.startswith("WITH"):
            df = pd.read_sql(sql, conn)
            if df.empty:
                result_text = "no rows selected"
            else:
                result_text = df.to_string(index=False)
        
        # B. DDL / DML -> Execute and Check Row Counts
        else:
            cursor.execute(sql)
            
            # Check for standard SQL*Plus-style feedback
            if clean_sql.startswith("CREATE"): 
                result_text = "Table created." # Server doesn't send this, we must mimic.
            elif clean_sql.startswith("DROP"): 
                result_text = "Table dropped."
            elif clean_sql.startswith("ALTER"): 
                result_text = "Table altered."
            elif clean_sql.startswith("PL/SQL") or clean_sql.startswith("BEGIN") or clean_sql.startswith("DECLARE"):
                result_text = "PL/SQL procedure successfully completed."
            
            # For DML (Insert/Update/Delete), use the REAL row count from the server
            elif clean_sql.startswith("INSERT"): 
                result_text = f"{cursor.rowcount} row(s) created."
            elif clean_sql.startswith("UPDATE"): 
                result_text = f"{cursor.rowcount} row(s) updated."
            elif clean_sql.startswith("DELETE"): 
                result_text = f"{cursor.rowcount} row(s) deleted."
            else:
                result_text = "Command executed successfully."

        # C. FETCH DBMS_OUTPUT (The "Real" Server Output)
        # If your PL/SQL block used dbms_output.put_line, we grab it here.
        chunk_size = 100
        lines_var = cursor.arrayvar(str, chunk_size)
        num_lines_var = cursor.var(int)
        num_lines_var.setvalue(0, chunk_size)
        
        while True:
            cursor.callproc("dbms_output.get_lines", (lines_var, num_lines_var))
            num_lines = num_lines_var.getvalue()
            if num_lines > 0:
                # Add the server's print output to our result
                fetched_lines = lines_var.getvalue()[:num_lines]
                extra_output = "\n".join([line for line in fetched_lines if line])
                if extra_output:
                    result_text += f"\n\n{extra_output}"
            else:
                break

        return result_text.strip()

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)  # Print full traceback to console
        
        # --- ERROR LOGGING ---
        if task_context:
            try:
                log_filename = "error_log.txt"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(log_filename, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] ERROR in Assignment: {task_context.get('assignment_name', 'Unknown')}\n")
                    f.write(f"Question: {task_context.get('question', 'N/A')}\n")
                    f.write(f"Query:\n{sql}\n")
                    f.write(f"Error Details:\n{traceback_str}\n")
                    f.write("-" * 50 + "\n")
            except Exception as log_err:
                print(f"Failed to write to error log: {log_err}")
                
        return f"ERROR:\n{e}"
    finally:
        cursor.close()

# ... (Keep everything above execute_sql_safely as it is) ...

def generate_assignment_markdown(output_filename="DBMS_Assignment.md"):
    print("--- Starting Assignment Auto-Solver (Markdown Mode) ---")
    
    # 1. Connect to DB
    try:
        conn = get_db_connection()
    except Exception as e:
        print("Fatal Error: Could not connect to database.")
        return

    # 2. Setup Directories
    # Create a folder for images so they don't clutter your root folder
    img_dir = "assignment_images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # 3. Start Markdown Content
    # We use standard Markdown for the top metadata
    md_content = f"""
# Database Management Systems - BCSE302P
**Name:** {USER_CONFIG["name"]}
**Reg. No. :** {USER_CONFIG['regno']}
**Slot :** {USER_CONFIG['slot']}
**Faculty :** {USER_CONFIG['faculty']}

***Lab {USER_CONFIG["labNo"]} - {USER_CONFIG['labTitle']}***

---
"""
    
    # Combine Setup and Assignment tasks
    all_tasks = SETUP_QUERIES + ASSIGNMENTS 
    
    print(f"\nProcessing {len(all_tasks)} queries...")
    
    # Track created tables
    created_tables = []
    created_views = []

    for i, item in enumerate(all_tasks):
        print(f"  > Processing Query {i+1}...")
        
        # Track table names if it is a CREATE statement
        sql_upper = item['sql'].strip().upper()
        if sql_upper.startswith("CREATE TABLE"):
            try:
                # Basic parsing: CREATE TABLE xyz ( ... or CREATE TABLE xyz AS ...
                parts = sql_upper.split()
                if len(parts) > 2:
                    # Remove potential open parenthesis if directly attached
                    table_name = parts[2].split('(')[0]
                    if table_name not in created_tables:
                        created_tables.append(table_name)
            except:
                pass
        
        # Track view names
        if "CREATE VIEW" in sql_upper or "CREATE OR REPLACE VIEW" in sql_upper:
            try:
                # Handle CREATE OR REPLACE VIEW vs CREATE VIEW
                start_marker = "VIEW"
                start_idx = sql_upper.find(start_marker)
                if start_idx != -1:
                    # Get the part after "VIEW "
                    remainder = sql_upper[start_idx + len(start_marker):].strip()
                    # The next word is the view name
                    view_name = remainder.split()[0]
                    if view_name not in created_views:
                        created_views.append(view_name)
            except:
                pass

        # A. Execute SQL
        task_ctx = {
            "assignment_name": f"{USER_CONFIG['labTitle']} (Lab {USER_CONFIG['labNo']})",
            "question": item.get('q', f'Task {i+1}')
        }
        result_str = execute_sql_safely(conn, item['sql'], task_context=task_ctx)

        # B. Create Image
        # Save explicitly into the folder
        img_filename = os.path.join(img_dir, f"q{i}.png")
        create_terminal_screenshot(item['sql'], result_str, img_filename)
        
        # To be flexible to markdown's web-url slashes
        # Convert Windows backslashes (\) to Web forward slashes (/)
        img_web_path = img_filename.replace("\\", "/")
        
        # C. Write to Markdown using HTML-Hybrid Syntax
        # This <div> prevents page breaks between Question and Image.
        # We use <h3> and <img> because standard Markdown (###, ![]) won't render inside a div.
        
        q_text = item.get('q', f'Task {i+1}')
        
        block = f"""
<div style="page-break-inside: avoid; margin-bottom: 30px; padding-bottom: 10px;">
    <h6>{q_text}</h6>
    <img src="{img_web_path}" alt="Output for {q_text}" style="border: 1px solid #333; max-width: 100%;">
</div>
"""
        md_content += block

    # 4. Save Markdown File
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 5. Cleanup created tables and views
    if created_tables or created_views:
        print("\n[Cleanup] Dropping temporary objects...")
        cursor = conn.cursor()
        
        # Drop Views first (good practice as they might depend on tables)
        for view in created_views:
            try:
                cursor.execute(f"DROP VIEW {view}")
                print(f"  [-] Dropped View: {view}")
            except oracledb.Error as e:
                if "ORA-00942" not in str(e): # View doesn't exist
                    print(f"  [!] Could not drop view {view}: {e}")

        # Drop Tables
        for table in reversed(created_tables): # Reverse order to handle foreign keys
            try:
                cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
                print(f"  [-] Dropped Table: {table}")
            except oracledb.Error as e:
                # ORA-00942: table or view does not exist (already dropped?)
                if "ORA-00942" not in str(e):
                    print(f"  [!] Could not drop table {table}: {e}")
        cursor.close()

    conn.close()
    print(f"\nSuccess! Generated '{output_filename}'")
    print(f"Images saved in: {os.path.abspath(img_dir)}")
    print("Open the .md file in Obsidian/VS Code and export to PDF.")

    
# ==========================================
#        PART 4: HELPER FUNCTIONS
# ==========================================

def _wrap_text(text, max_chars=100):
    """Wrap lines longer than max_chars."""
    lines = text.split('\n')
    wrapped = []
    for line in lines:
        while len(line) > max_chars:
            # Try to break at a space
            break_at = line.rfind(' ', 0, max_chars)
            if break_at == -1:
                break_at = max_chars
            wrapped.append(line[:break_at])
            line = '  ' + line[break_at:].lstrip()
        wrapped.append(line)
    return '\n'.join(wrapped)

if __name__ == "__main__":
    # We call the new Markdown function instead of the PDF one
    set_user_config()
    generate_assignment_markdown()