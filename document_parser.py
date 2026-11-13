import io
from typing import Optional

def extract_text_from_file(file_bytes: bytes, file_name: str) -> str:
    """
    Trích xuất văn bản từ nhiều định dạng: PDF, DOCX, XLSX, TXT
    """
    ext = file_name.split(".")[-1].lower()
    
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
        
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- TRANG {idx+1} ---\n{page_text}")
            return "\n".join(text)
        except Exception as e:
            return f"[Lỗi khi đọc file PDF: {str(e)}]"
            
    elif ext in ["docx", "doc"]:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    full_text.append(" | ".join(row_data))
            return "\n".join(full_text)
        except Exception as e:
            return f"[Lỗi khi đọc file Word DOCX: {str(e)}]"
            
    elif ext in ["xlsx", "xls"]:
        try:
            import pandas as pd
            xl = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
            full_text = []
            for sheet_name, df in xl.items():
                full_text.append(f"--- SHEET: {sheet_name} ---")
                full_text.append(df.to_string())
            return "\n".join(full_text)
        except Exception as e:
            return f"[Lỗi khi đọc file Excel: {str(e)}]"
            
    else:
        return f"[Định dạng file .{ext} chưa được hỗ trợ. Vui lòng dán văn bản trực tiếp.]"

