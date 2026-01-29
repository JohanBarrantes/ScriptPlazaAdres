from dotenv import load_dotenv
import os
import camelot
import pandas as pd
import re
import unicodedata
from sqlalchemy import create_engine
from datetime import datetime 

PDF_FOLDER = "data/pdfs"

load_dotenv()

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
FILE_NAME = os.getenv("FILE_NAME")

DB_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(DB_URL)

def main() -> None:
    """
    Start point of the application
    """
    if not os.path.exists(PDF_FOLDER):
        print(f"Folder '{PDF_FOLDER}' does not exist")
        return

    pdf_files = get_pdf_files(PDF_FOLDER)
    print(f"Count PDFs: {len(pdf_files)}")

    if not pdf_files:
        print("There are no PDF files to process")
        return

    total_tables = 0
    total_rows = 0

    for pdf in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf)
        tables_count, rows_count = process_pdf(pdf_path)
        total_tables += tables_count
        total_rows += rows_count

    print(f"\nFinished processing {len(pdf_files)} PDFs")
    print(f"Total rows inserted: {total_rows}")

def get_pdf_files(folder_path: str) -> list:
    """List of PDF files in a folder"""
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

def process_pdf(pdf_path: str) -> tuple:
    """
    Read PDF, extract tables, print content, and insert into PostgreSQL
    Returns number of tables and total rows inserted
    """
    print(f"\nProcessing: {os.path.basename(pdf_path)}")
    tables_inserted = 0
    rows_inserted = 0

    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        print(f"Tables found: {tables.n}")

        if tables.n == 0:
            print("Warning: No tables found")
            return (0, 0)

        all_tables_df = pd.DataFrame()
        
        year = str(datetime.now().year)
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1 
        for index, table in enumerate(tables):
            df = table.df

            df.columns = [to_snake_case(col) for col in df.iloc[0]]

            print(f"XXXXXXX '{df.columns}'")
            df = df[1:]
            df.reset_index(drop=True, inplace=True)
            df = df.dropna(how='all')
            df = df[df.notna().any(axis=1)]
            df = df.apply(lambda col: col.str.replace('\n', ' ') if col.dtype == "object" else col)

            df['año'] = year
            df['trimestre'] = quarter
            df['activo'] = 1
            all_tables_df = pd.concat([all_tables_df, df], ignore_index=True)
            
        if not all_tables_df.empty:
            table_name = f"{FILE_NAME}".lower()
            all_tables_df.to_sql(table_name, con=engine, if_exists="replace", index=False)
            print(f"Inserted unified table into PostgreSQL as '{table_name}'")

            tables_inserted += 1
            rows_inserted += len(all_tables_df)

    except Exception as error:
        print("Error processing the PDF")
        print(error)

    return (tables_inserted, rows_inserted)

def to_snake_case(column_name):
    # Asegurarse de que el nombre de la columna sea una cadena
    column_name = str(column_name)
    
    # Eliminar tildes (acentos) usando unicodedata
    column_name = unicodedata.normalize('NFKD', column_name).encode('ascii', 'ignore').decode('utf-8')
    
    # Reemplazar saltos de línea y espacios por guiones bajos
    column_name = re.sub(r'[\n\s]+', '_', column_name)
    
    # Reemplazar caracteres no alfanuméricos ni guiones bajos
    column_name = re.sub(r'[^a-z0-9_]', '', column_name.lower())
    
    return column_name

if __name__ == "__main__":
    main()
