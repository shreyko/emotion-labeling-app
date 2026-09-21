import json
import os

print("--- Streamlit Secrets Setup ---")
json_path = input("Drag and drop your Google Service Account JSON file here (or type the path): ").strip().strip('\'"')
sheet_url = input("Paste the full URL of your Google Sheet: ").strip()

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    os.makedirs(".streamlit", exist_ok=True)
    
    with open(".streamlit/secrets.toml", "w") as f:
        f.write("[connections.gsheets]\n")
        f.write(f'spreadsheet = "{sheet_url}"\n')
        
        for key, value in data.items():
            # Handle newlines in the private key correctly for TOML
            v_str = str(value).replace('\n', '\\n')
            f.write(f'{key} = "{v_str}"\n')
            
    print("\nSuccess! Generated .streamlit/secrets.toml successfully.")
    print("You are now ready to test the app locally!")
except Exception as e:
    print(f"\nError: {e}")
