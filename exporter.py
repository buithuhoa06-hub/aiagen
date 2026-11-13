import io
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_bid_docx(project_data: dict) -> io.BytesIO:
    doc = docx.Document()
    
    # Margin
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # 1. Header Công ty
    header_para = doc.add_paragraph()
    r1 = header_para.add_run("CÔNG TY CỔ PHẦN CÔNG NGHỆ THIÊN MINH\n")
    r1.bold = True
    r1.font.size = Pt(13)
    r1.font.color.rgb = RGBColor(13, 59, 102)
    
    r2 = header_para.add_run("Địa chỉ: Tầng 8, Tòa nhà Thiên Minh, Hà Nội | Hotline: (024) 3888-9999\n")
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(100, 100, 100)
    
    # Tiêu đề
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run("\nHỒ SƠ ĐỀ XUẤT GIẢI PHÁP & BẢN CHÀO GIÁ DỰ ÁN\n")
    title_run.bold = True
    title_run.font.size = Pt(16)
    title_run.font.color.rgb = RGBColor(0, 95, 115)
    
    # Kính gửi
    p_to = doc.add_paragraph()
    p_to.add_run(f"Kính gửi: ").bold = True
    p_to.add_run(f"Ban Quản lý Dự án - {project_data.get('client', 'Quý Khách hàng')}\n")
    p_to.add_run(f"Dự án: ").bold = True
    p_to.add_run(f"{project_data.get('project_name', 'Cung cấp thiết bị mạng & dịch vụ')}\n")
    p_to.add_run(f"Ngày phát hành: ").bold = True
    p_to.add_run(f"{datetime.now().strftime('%d/%m/%Y')}\n")

    # 2. Bảng Ma trận Tuân thủ Kỹ thuật
    doc.add_heading("1. MA TRẬN ĐÁP ỨNG TIÊU CHUẨN KỸ THUẬT (COMPLIANCE MATRIX)", level=2)
    
    comp_matrix = project_data.get("compliance_matrix", [])
    if comp_matrix:
        table_comp = doc.add_table(rows=1, cols=4)
        table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_cells = table_comp.rows[0].cells
        hdr_cells[0].text = "Hạng mục / Cấu hình"
        hdr_cells[1].text = "Số lượng"
        hdr_cells[2].text = "Đánh giá Đáp ứng"
        hdr_cells[3].text = "Ghi chú Năng lực"
        
        for cell in hdr_cells:
            set_cell_background(cell, "005F73")
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.bold = True
                    run.font.size = Pt(10)
                    
        for row in comp_matrix:
            row_cells = table_comp.add_row().cells
            row_cells[0].text = str(row.get("Hạng mục", ""))
            row_cells[1].text = str(row.get("Số lượng", ""))
            row_cells[2].text = str(row.get("Đáp ứng (Compliance)", ""))
            row_cells[3].text = str(row.get("Đánh giá Rủi ro", ""))
            for cell in row_cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)

    # 3. Bảng Bóc tách Giá trị
    doc.add_heading("\n2. BẢNG BÓC TÁCH CHI PHÍ ĐỀ XUẤT", level=2)
    pricing_rows = project_data.get("pricing_rows", [])
    if pricing_rows:
        table_price = doc.add_table(rows=1, cols=5)
        table_price.alignment = WD_TABLE_ALIGNMENT.CENTER
        p_hdr = table_price.rows[0].cells
        p_hdr[0].text = "STT"
        p_hdr[1].text = "Tên Thiết bị / Dịch vụ"
        p_hdr[2].text = "SL"
        p_hdr[3].text = "Đơn giá (VNĐ)"
        p_hdr[4].text = "Thành tiền (VNĐ)"
        
        for cell in p_hdr:
            set_cell_background(cell, "0D3B66")
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.bold = True
                    run.font.size = Pt(10)
                    
        for idx, item in enumerate(pricing_rows, 1):
            r_cells = table_price.add_row().cells
            r_cells[0].text = str(idx)
            r_cells[1].text = str(item.get("Tên Hạng mục", ""))
            r_cells[2].text = str(item.get("SL Yêu cầu", ""))
            r_cells[3].text = f"{item.get('Đơn giá niêm yết (VNĐ)', 0):,.0f}"
            r_cells[4].text = f"{item.get('Thành tiền (VNĐ)', 0):,.0f}"
            for cell in r_cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)

    # 4. Tổng cộng và chiết khấu
    doc.add_paragraph()
    summary_p = doc.add_paragraph()
    summary_p.add_run(f"- Tổng giá trị thiết bị & dịch vụ niêm yết: ").bold = True
    summary_p.add_run(f"{project_data.get('total_list_price', 0):,.0f} VNĐ\n")
    summary_p.add_run(f"- Mức chiết khấu thương mại ({project_data.get('discount_pct', 0)}%): ").bold = True
    summary_p.add_run(f"- {project_data.get('discount_amount', 0):,.0f} VNĐ\n")
    
    final_p = doc.add_paragraph()
    r_fin = final_p.add_run(f"👉 TỔNG GIÁ TRỊ THANH TOÁN (Chưa gồm VAT): {project_data.get('final_price', 0):,.0f} VNĐ")
    r_fin.bold = True
    r_fin.font.size = Pt(12)
    r_fin.font.color.rgb = RGBColor(180, 0, 0)

    # 5. Tiến độ & SLA
    doc.add_heading("3. TIẾN ĐỘ THỰC HIỆN VÀ CAM KẾT DỊCH VỤ", level=2)
    doc.add_paragraph(f"- Thời hạn hoàn thành bàn giao: {project_data.get('deadline_days', 10)} ngày làm việc.")
    doc.add_paragraph(f"- Tiêu chuẩn dịch vụ hỗ trợ (SLA): {project_data.get('sla_requirement', 'Tiêu chuẩn')}.")

    # 5b. Các điều chỉnh minh bạch gửi khách hàng (nếu có)
    change_notices = project_data.get("customer_change_notices", [])
    if change_notices:
        doc.add_heading("4. CÁC ĐIỂM ĐIỀU CHỈNH SO VỚI YÊU CẦU BAN ĐẦU (ĐỀ XUẤT THƯƠNG LƯỢNG)", level=2)
        p_note = doc.add_paragraph("Để đảm bảo tính khả thi về kỹ thuật, tiến độ và chính sách thương mại, Thiên Minh xin thông báo minh bạch các điểm điều chỉnh so với đề nghị ban đầu của Quý khách:")
        for idx, notice in enumerate(change_notices, 1):
            doc.add_paragraph(f"  {idx}. {notice}")

    # 6. Chữ ký
    doc.add_paragraph("\n\n")
    table_sign = doc.add_table(rows=2, cols=2)
    table_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    s1 = table_sign.rows[0].cells[0].paragraphs[0]
    s1.add_run("ĐẠI DIỆN KHÁCH HÀNG\n").bold = True
    s1.add_run("(Ký, ghi rõ họ tên)")
    s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    s2 = table_sign.rows[0].cells[1].paragraphs[0]
    s2.add_run("ĐẠI DIỆN CÔNG TY THIÊN MINH\n").bold = True
    s2.add_run("(Ký tên và đóng dấu)")
    s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

