import getpass
import os

def get_user_configuration():
    print("---------------------------------------------------------")
    print("       Automatic Assignment Configuration                ")
    print("---------------------------------------------------------")
    print("Please enter the following details to configure the application.")
    print("---------------------------------------------------------")

    config = {}

    # API Configuration
    print("\n[API Configuration]")
    config["gemini_api_key"] = input("Enter Google Gemini API Key: ").strip()

    # Database Configuration
    print("\n[Database Configuration]")
    config["db_user"] = input("Oracle DB User [system]: ").strip() or "system"
    config["db_password"] = getpass.getpass("Oracle DB Password [manager]: ").strip() or "manager"
    config["db_service"] = input("Oracle Service Name [xe]: ").strip() or "xe"
    config["db_host"] = input("Database Host [localhost]: ").strip() or "localhost"
    config["db_port"] = input("Database Port [1521]: ").strip() or "1521"

    # User Details
    print("\n[Student Details]")
    config["regno"] = input("Registration Number [YYBBBXXXX]: ").strip() or "YYBBBXXXX"
    config["name"] = input("Student Name [Superman]: ").strip() or "Superman"
    config["lab_no"] = input("Lab Number [0]: ").strip() or "0"
    config["lab_title"] = input("Lab Title [Practice Exercise]: ").strip() or "Practice Exercise"
    config["faculty"] = input("Faculty Name [facc]: ").strip() or "facc"
    config["slot"] = input("Slot [L00-L00]: ").strip() or "L00-L00"

    # Assignment Details
    print("\n[Assignment Details]")
    # Ask for absolute path, defaulting to local Lab-Exercises/assn.pdf
    default_path = os.path.abspath("Lab-Exercises/assn.pdf")
    user_path = input(f"Absolute Path to Assignment PDF [{default_path}]: ").strip("\"")
    
    # Remove quotes if user added them
    if user_path.startswith('"') and user_path.endswith('"'):
        user_path = user_path[1:-1]
        
    config["assn_path"] = user_path or default_path

    print("\n---------------------------------------------------------")
    print("Configuration captured successfully.")
    print("---------------------------------------------------------")
    
    return config
