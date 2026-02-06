import os
import re
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

# ==========================================
# FILE OPERATIONS
# ==========================================

def save_uploaded_file(uploaded_file, folder_path: str) -> Optional[str]:
    """
    Saves an uploaded file to the specified directory.
    
    Args:
        uploaded_file: The file object from Streamlit uploader.
        folder_path (str): Destination directory path.
        
    Returns:
        Optional[str]: Full path of the saved file or None if failed.
    """
    if uploaded_file is not None:
        try:
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        except Exception as e:
            st.error(f"Erro ao salvar arquivo: {e}")
            return None
    return None

# ==========================================
# VALIDATION
# ==========================================

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.
    
    Args:
        email (str): Email string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not email: return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# ==========================================
# DATA PERSISTENCE (JSONL + EXCEL)
# ==========================================

def save_to_jsonl(data: Dict[str, Any], filename: str = "bmed_submissions.jsonl") -> bool:
    """
    Appends a dictionary as a JSON line to a file.
    Preferred for raw data backup.
    """
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar backup JSONL: {e}")
        return False

def save_to_excel_db(data: Dict[str, Any], filename: str = "bmed_startups_database.xlsx") -> bool:
    """
    Saves submission data to an Excel file, separating by Cluster (Sheet).
    
    Args:
        data (Dict): The flat or nested dictionary of submission data.
        filename (str): The Excel filename.
    
    Returns:
        bool: True if successful.
    """
    try:
        # 1. Flatten Data: Merge specific_data into main dict for tabular format
        flat_data = data.copy()
        specific = flat_data.pop('specific_data', {})
        flat_data.update(specific)
        
        # 2. Identify Target Sheet (Cluster)
        # Use a safe default if cluster is missing
        cluster_name = flat_data.get('cluster_macro', 'Outros')
        # Excel sheet names have limits (31 chars). Truncate if needed.
        sheet_name = cluster_name[:31] 

        # 3. Create DataFrame for current entry
        new_df = pd.DataFrame([flat_data])

        # 4. Load or Create Workbook logic
        if os.path.exists(filename):
            # Load existing excel file
            # We need to use openpyxl engine to not overwrite other sheets
            # But pandas 'ExcelWriter' with mode='a' is the pythonic way
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                # Check if sheet exists to append properly
                try:
                    # Try to load existing sheet to get headers and append
                    existing_df = pd.read_excel(filename, sheet_name=sheet_name)
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                except ValueError:
                    # Sheet doesn't exist yet, simply write it
                    new_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Create new file
            with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
                new_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True

    except Exception as e:
        st.error(f"Erro ao atualizar planilha Excel: {e}")
        return False
