import getpass

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

    print("\n---------------------------------------------------------")
    print("Configuration captured successfully.")
    print("---------------------------------------------------------")
    
    return config
