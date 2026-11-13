import os
import json
import re
from dotenv import load_dotenv

# Nạp API Key từ file .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

def get_gemini_client():
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        print(f"Lỗi khởi tạo Gemini API: {str(e)}")
        return None

def extract_rfp_with_gemini(rfp_text: str, catalog_items: list) -> dict:
    """
    Sử dụng Gemini LLM để đọc hiểu và bóc tách cấu trúc yêu cầu RFP
    """
    model = get_gemini_client()

    catalog_summary = "\n".join([
        f"- SKU: {c['sku']} | Tên: {c['name']} | Giá: {c['unit_price']:,}đ | Kho: {c['stock']} | Nhóm: {c.get('category')}"
        for c in catalog_items
    ])

    system_prompt = f"""
Bạn là Chuyên gia AI Phân tích Hồ sơ Chào giá (RFP Shredder) của Công ty Công nghệ Thiên Minh.
Nhiệm vụ của bạn là đọc văn bản yêu cầu dự án sau đây từ khách hàng, bóc tách chính xác các thông tin cấu trúc và đối chiếu với Danh mục sản phẩm của Thiên Minh.

DANH MỤC THIẾT BỊ & DỊCH VỤ CỦA THIÊN MINH:
{catalog_summary}

VĂN BẢN YÊU CẦU TỪ KHÁCH HÀNG:
\"\"\"
{rfp_text}
\"\"\"

HƯỚNG DẪN BẮT BUỘC:
1. Kiểm tra tính đầy đủ (Completeness Check):
   - Phải có tối thiểu 1 thiết bị/dịch vụ rõ ràng kèm số lượng.
   - Phải có thời hạn triển khai/bàn giao (deadline) dự kiến.
   - Nếu thiếu một trong hai thông tin này, đánh dấu is_sufficient = false và liệt kê cụ thể vào missing_fields.
2. Trích xuất danh mục thiết bị:
   - Cố gắng tìm mã SKU tương ứng trong danh mục của Thiên Minh.
   - Nếu khách yêu cầu thiết bị ngoài danh mục, ghi rõ sku="OUT_OF_CATALOG" và điền tên thiết bị.
   - Ước tính số ngày công kỹ thuật (mandays) cho mỗi hạng mục (Core switch: 2 công/con, Access switch: 0.5 công/con, Firewall: 3 công/con).
3. Trích xuất mức chiết khấu đề nghị (discount_requested_pct): Nếu không có, mặc định là 0.
4. Trích xuất yêu cầu SLA bảo trì: Ví dụ "24/7/2h Onsite", "8x5 NBD", hoặc "Tiêu chuẩn".

HÃY TRẢ VỀ KẾT QUẢ DƯỚI DẠNG ĐÚNG MỘT ĐỐI TƯỢNG JSON (KHÔNG KÈM TEXT GIẢI THÍCH):
{{
  "client_name": "Tên công ty / khách hàng nếu tìm thấy, không có để trống",
  "budget_vnd": float (ngân sách quy đổi ra VNĐ, nếu không có để 0),
  "is_sufficient": true hoặc false,
  "missing_fields": ["danh sách thông tin còn thiếu"],
  "deadline_days": int (ví dụ 10, 12, nếu không có để 0),
  "discount_requested_pct": float (ví dụ 4.0, 8.5, 0.0),
  "sla_requirement": "chuỗi mô tả SLA",
  "items": [
    {{
      "sku": "mã SKU trong catalog hoặc OUT_OF_CATALOG",
      "name": "tên thiết bị",
      "spec": "thông số kỹ thuật trích được",
      "mandatory": "điều kiện bắt buộc nếu có",
      "qty": int,
      "mandays": float
    }}
  ]
}}
"""

    if model:
        try:
            response = model.generate_content(
                system_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            raw_json = response.text.strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
            return json.loads(raw_json)
        except Exception as e:
            print(f"Lỗi khi gọi Gemini API: {str(e)}. Đang chuyển về Rule Engine dự phòng...")

    # FALLBACK DỰ PHÒNG
    text_lower = rfp_text.lower()
    missing = []
    if "ngày" not in text_lower and "tháng" not in text_lower:
        missing.append("Thời hạn triển khai / Deadline bàn giao")
    if not any(char.isdigit() for char in text_lower):
        missing.append("Số lượng cụ thể cho từng hạng mục")
    if "switch" not in text_lower and "firewall" not in text_lower and "wifi" not in text_lower:
        missing.append("Thông số kỹ thuật/mã thiết bị rõ ràng")

    is_sufficient = len(missing) == 0

    def extract_qty(pattern, default_qty):
        m = re.search(rf"(\d+)\s*(?:cái|con|chiếc|bộ|thiết bị|switch|firewall|access point|ap)?\s*{pattern}", text_lower)
        return int(m.group(1)) if m else default_qty

    items = []
    if "fortigate 100f" in text_lower or "fg-100f" in text_lower or "firewall" in text_lower:
        q = extract_qty(r"(?:thiết bị\s+)?(?:firewall|fortinet|fortigate)", 1)
        items.append({"sku": "FORTI-FG-100F", "name": "Firewall Fortinet FortiGate 100F", "qty": q, "mandays": q * 3.0})
    if "c9300x" in text_lower or "9300x" in text_lower or "quang core" in text_lower:
        q = extract_qty(r"(?:switch\s+)?(?:cisco\s+)?(?:catalyst\s+)?c?9300x", 2)
        items.append({"sku": "CISCO-C9300X-24Y", "name": "Switch Cisco Catalyst 9300X 24Y Core", "qty": q, "mandays": q * 2.0})
    if "9300 48" in text_lower or "c9300-48p" in text_lower or "48-port" in text_lower:
        q = extract_qty(r"(?:switch\s+)?(?:cisco\s+)?(?:catalyst\s+)?c?9300", 4)
        items.append({"sku": "CISCO-C9300-48P", "name": "Switch Cisco Catalyst 9300 48-Port PoE+", "qty": q, "mandays": q * 1.0})
    if "catalyst 1000" in text_lower or "c1000" in text_lower or "24-port poe+" in text_lower:
        q = extract_qty(r"(?:switch\s+)?(?:cisco\s+)?(?:catalyst\s+)?(?:1000|c1000)", 4)
        items.append({"sku": "CISCO-C1000-24P", "name": "Switch Cisco Catalyst 1000 24-Port PoE+", "qty": q, "mandays": q * 0.5})
    if "aruba" in text_lower or "ap-515" in text_lower or "wi-fi 6" in text_lower or "wifi 6" in text_lower:
        q = extract_qty(r"(?:access point\s+)?(?:aruba|ap-?515|wi-?fi)", 5)
        items.append({"sku": "ARUBA-AP-515", "name": "Access Point Aruba AP-515 Wi-Fi 6", "qty": q, "mandays": round(q * 0.3, 1)})

    items.append({
        "sku": "SVC-INSTALL-MANDAY",
        "name": "Dịch vụ Kỹ thuật cấu hình mạng & nghiệm thu",
        "qty": max(1, int(round(sum(i["mandays"] for i in items)))) if items else 3,
        "mandays": 0
    })

    disc_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text_lower)
    discount_val = float(disc_match.group(1)) if disc_match else 0.0

    dl_match = re.search(r"(\d+)\s*ngày", text_lower)
    deadline_val = int(dl_match.group(1)) if dl_match else 10

    # Trích xuất tên khách hàng và ngân sách từ văn bản raw
    client_match = re.search(r"(?:khách hàng|công ty|tập đoàn|ngân hàng|bệnh viện|đơn vị)\s*[:\-]?\s*([^\n\r,.:;]{4,60})", rfp_text, re.IGNORECASE)
    extracted_client = client_match.group(0).strip() if client_match else ""
    extracted_client = re.split(r"\s+(?:cần|đang|muốn|xin|gửi)\b", extracted_client, maxsplit=1, flags=re.IGNORECASE)[0].strip()

    budget_vnd = 0.0
    bm = re.search(r"ngân sách[^0-9]{0,20}(\d+(?:[.,]\d+)?)\s*(tỷ|triệu|tr)?", text_lower)
    if bm:
        b_val = float(bm.group(1).replace(",", "").replace(".", ""))
        unit = bm.group(2) or ""
        if "tỷ" in unit:
            b_val *= 1_000_000_000
        elif "triệu" in unit or "tr" in unit or b_val < 10_000:
            b_val *= 1_000_000
        budget_vnd = b_val

    sla_type = "24/7/2h Onsite" if "2h" in text_lower or "2 giờ" in text_lower else "8x5 Tiêu chuẩn NBD"

    return {
        "client_name": extracted_client,
        "budget_vnd": budget_vnd,
        "is_sufficient": is_sufficient,
        "missing_fields": missing,
        "deadline_days": deadline_val,
        "discount_requested_pct": discount_val,
        "sla_requirement": sla_type,
        "items": items
    }


def chat_with_assistant(user_message: str, chat_history: list, current_context: dict, config_data: dict) -> str:
    """
    Trợ lý Chatbot AI hiểu ngữ cảnh hồ sơ hiện tại, bảng giá và quy tắc duyệt của Thiên Minh.
    """
    catalog_items = config_data.get("catalog", [])
    approval_rules = config_data.get("approval_rules", {})
    ops_cap = config_data.get("operations_capacity", {})

    catalog_text = "\n".join([
        f"- {c['sku']}: {c['name']} | Giá {c['unit_price']:,} VNĐ | Tồn kho: {c['stock']} | Lead-time: {c['lead_time_days']} ngày"
        for c in catalog_items
    ])

    context_str = json.dumps(current_context, ensure_ascii=False, indent=2) if current_context else "Chưa có hồ sơ nào được phân tích."

    history_str = "\n".join([
        f"{'Người dùng' if m['role']=='user' else 'Trợ lý AI'}: {m['content']}"
        for m in chat_history[-6:]
    ])

    prompt = f"""
Bạn là **Trợ lý AI Pre-Sales & Thẩm định Dự án** của Công ty Cổ phần Công nghệ Thiên Minh.
Hãy trả lời câu hỏi của nhân viên kinh doanh/quản lý một cách **ngắn gọn, rõ ràng, thực tế, có gạch đầu dòng dễ đọc**.

DỮ LIỆU DANH MỤC & TỒN KHO HIỆN TẠI:
{catalog_text}

QUY ĐỊNH THẨM QUYỀN DUYỆT:
- Sales tự quyết: Chiết khấu <= {approval_rules.get('sales_rep', {}).get('max_discount_pct', 5)}%
- Trưởng phòng KD: Chiết khấu <= {approval_rules.get('sales_manager', {}).get('max_discount_pct', 10)}% hoặc SLA khẩn cấp 24/7/2h
- Ban Giám đốc: Chiết khấu > 10%, thiết bị ngoài danh mục hoặc trễ tiến độ
- Quỹ công kỹ thuật còn trống trong tháng: {ops_cap.get('total_capacity_mandays', 110) - ops_cap.get('booked_mandays_current_month', 68)} mandays

HỒ SƠ DỰ ÁN ĐANG MỞ TRÊN MÀN HÌNH:
{context_str}

LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY:
{history_str}

CÂU HỎI MỚI CỦA NGƯỜI DÙNG:
"{user_message}"
"""

    model = get_gemini_client()
    if model:
        try:
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            print(f"Lỗi Chatbot Gemini API: {str(e)}")

    # FALLBACK THÔNG MINH THEO NGỮ CẢNH KHI KHÔNG GỌI ĐƯỢC API
    q = user_message.lower()
    if "rủi ro" in q or "tóm tắt" in q or "phân tích" in q:
        if not current_context:
            return "Hiện chưa có hồ sơ nào được phân tích. Bạn hãy chọn một kịch bản mẫu hoặc tải file RFP ở khung bên trái và nhấn **Phân tích Yêu cầu** nhé!"
        if not current_context.get("is_sufficient", True):
            missing = ", ".join(current_context.get("missing_fields", []))
            return f"⚠️ **Rủi ro lớn nhất của hồ sơ này:** Đang **thiếu thông tin bắt buộc** ({missing}). Tuyệt đối chưa nên báo giá mà cần gửi email RFI hỏi khách hàng làm rõ trước."
        esc = current_context.get("escalations", [])
        if esc:
            return f"📋 **Tóm tắt đánh giá hồ sơ {current_context.get('client', '')}:**\n- **Giá chào:** {current_context.get('final_price', 0):,.0f} VNĐ (CK {current_context.get('discount_pct', 0)}%)\n- **Cấp duyệt:** {current_context.get('approval_level')}\n- **Điểm cần lưu ý:**\n" + "\n".join([f"  • {x}" for x in esc])
        return f"✅ Hồ sơ **{current_context.get('client', '')}** hoàn toàn khả thi! Giá chào: **{current_context.get('final_price', 0):,.0f} VNĐ**, nằm trong quyền tự quyết của Sales."

    if "duyệt" in q or "thẩm quyền" in q or "chiết khấu" in q:
        return (
            "📜 **Quy định phân quyền duyệt của Thiên Minh:**\n"
            "- **Sales tự quyết:** Chiết khấu `≤ 5%`, đủ tồn kho, đúng tiến độ và SLA tiêu chuẩn.\n"
            "- **Trưởng phòng KD duyệt:** Chiết khấu `5.1% – 10%` hoặc có cam kết SLA khẩn cấp `24/7/2h`.\n"
            "- **Ban Giám đốc duyệt:** Chiết khấu `> 10%`, có thiết bị ngoài danh mục hoặc quá tải lịch kỹ thuật."
        )

    if "tồn kho" in q or "giá" in q or "thiết bị" in q or "catalog" in q:
        lines = ["📦 **Danh mục thiết bị & tồn kho sẵn có tại Thiên Minh:**"]
        for c in catalog_items:
            lines.append(f"- **{c['sku']}** ({c['name']}): Giá `{c['unit_price']:,.0f} đ` | Tồn kho: **{c['stock']}** | Giao trong {c['lead_time_days']} ngày")
        return "\n".join(lines)

    if "thương lượng" in q or "đàm phán" in q or "tư vấn" in q:
        return (
            "💡 **Gợi ý đàm phán với khách hàng:**\n"
            "1. Nếu khách đòi chiết khấu cao (> 5%), hãy đề nghị điều kiện đổi lại như **tạm ứng 50% ngay khi ký hợp đồng**.\n"
            "2. Nếu thiếu tồn kho một vài mã thiết bị, đề xuất **giao hàng làm 2 đợt** (đợt 1 giao hàng sẵn có để kịp tiến độ, đợt 2 giao phần nhập thêm).\n"
            "3. Với SLA 24/7/2h, nhấn mạnh đây là gói bảo vệ đặc biệt và giải thích rõ chi phí nhân lực ứng trực đi kèm."
        )

    return (
        "Tôi là **Trợ lý AI Thiên Minh**. Bạn có thể hỏi tôi về:\n"
        "- *\"Tóm tắt rủi ro của hồ sơ đang mở?\"*\n"
        "- *\"Kiểm tra tồn kho và giá thiết bị Cisco / Fortinet\"*\n"
        "- *\"Tại sao hồ sơ này phải chuyển Trưởng phòng duyệt?\"*\n"
        "- *\"Gợi ý cách đàm phán chiết khấu với khách hàng\"*"
    )
