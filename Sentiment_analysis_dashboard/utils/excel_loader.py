import pandas as pd
import os

# ===============================
# CONFIG
# ===============================
EXCEL_FILE = r"data\Sentimental_analysis_masked.xlsx"

# ===============================
# PURE DATA LOADER (NO FILTERS)
# ===============================
def load_excel_data():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        return pd.DataFrame()

    try:
        # Load the Excel file
        df = pd.read_excel(EXCEL_FILE)
        
        if df.empty:
            return pd.DataFrame()

        # ===============================
        # CLEANING & HEADERS (Consistent with gsheet_loader)
        # ===============================
        # Ensure column names are stripped of whitespace
        df.columns = [str(c).strip() if c else f"unnamed_{i}" for i, c in enumerate(df.columns)]
        
        # Handle duplicate headers if any (though pandas handles this, we stay consistent)
        seen = {}
        new_cols = []
        for col in df.columns:
            if col in seen:
                seen[col] += 1
                new_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_cols.append(col)
        df.columns = new_cols

        # ===============================
        # TYPE CASTING (SAFE)
        # ===============================
        for col in ["created", "closed", "modified"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        for col in ["Sentiment Score", "resolution_hours", "response_time_seconds"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df
        
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return pd.DataFrame()
