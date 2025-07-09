import datetime
import os
import subprocess
import sys
var = os.getenv('passwd_platinum')

# --- Configuration ---
# IMPORTANT:
# 1. Replace 'your_mysql_username' and 'your_mysql_password' with your actual MySQL credentials.
# 2. Replace 'your_database_name1', 'your_database_name2', etc., with the names of the databases you want to backup.
# 3. Ensure BACKUP_DIR is a valid directory where you want to store your backups.

# Path Ke mysqldump 
MYSQLDUMP_PATH = r"D:\xampp\mysql\bin\mysqldump.exe"

# Directory Dimana File Backup Bkl Kesimpen
BACKUP_DIR = r"D:\MySQL_Backups"

# MySQL database credentials
DB_USER = "root"  # Your MySQL username (e.g., 'root' for XAMPP default)
DB_PASSWORD = str(var) # Your MySQL password. If there's no password, leave it as an empty string.

DATABASES_TO_BACKUPS = ["db_platinum_spa"] # bisa tambah lagi klo mw. ksh , aja
# End Config

def backup_db(db_name):
  print(f"Mencoba Backup DB {db_name}")

  # Buat Timestamp
  timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

  # Buat Nama FIle
  backup_file_name = f"{db_name}_{timestamp}.sql"
  full_backup_path = os.path.join(BACKUP_DIR, backup_file_name)

  # Pastikan Folder Backup Ada, klo g ad buat baru
  try:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print("Pastikan Folder ada")
  except OSError as e:
    print(f"Gagal Buat Folder '{BACKUP_DIR}': {e}")
  
  # Construct the mysqldump command.
  # The --password flag should be followed immediately by the password without a space.
  # If DB_PASSWORD is empty, the --password flag is omitted.
  command = [
      MYSQLDUMP_PATH,
      f"--user={DB_USER}"
  ]
  if DB_PASSWORD:
    command.append(f"--password={DB_PASSWORD}")

  command.extend([
    db_name,
    f"--result-file={full_backup_path}"
  ])

  try:
    # Execute the mysqldump command
    # subprocess.run is generally preferred for simple command execution.
    # check=True raises CalledProcessError if the command returns a non-zero exit code.
    print(f"Executing command: {' '.join(command)}")
    result = subprocess.run(command, check=True, capture_output=True, text=True)

    print(f"Successfully backed up '{db_name}' to '{full_backup_path}'")
    # print(f"mysqldump stdout: {result.stdout}") # Uncomment for debugging
    # print(f"mysqldump stderr: {result.stderr}") # Uncomment for debugging

  except FileNotFoundError:
    print(f"ERROR: mysqldump not found at '{MYSQLDUMP_PATH}'.")
    print("Please verify the 'MYSQLDUMP_PATH' in the script is correct.")
    sys.exit(1) # Exit with error code if mysqldump is not found
  except subprocess.CalledProcessError as e:
    print(f"ERROR: Failed to backup '{db_name}'.")
    print(f"Command: {e.cmd}")
    print(f"Return Code: {e.returncode}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
    print("Please check your MySQL username, password, database name, and permissions.")
    sys.exit(1) # Exit with error code for command execution errors
  except Exception as e:
    print(f"An unexpected error occurred during backup of '{db_name}': {e}")
    sys.exit(1) # Exit with a generic error code

def main():
  """Main function to orchestrate the database backup process."""
  if not DATABASES_TO_BACKUPS:
    print("No databases specified for backup.")
    print("Please edit 'backup_databases.py' and add database names to 'DATABASES_TO_BACKUP' list.")
    sys.exit(1)
  print("--- Starting MySQL Database Backup Process ---")
  
  for db in DATABASES_TO_BACKUPS:
    backup_db(db)

  print("--- Database backup process completed. ---")

if __name__ == "__main__":
  main()
  








