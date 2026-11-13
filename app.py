import streamlit as st
import yaml
import os
import pandas as pd

# Import modules nội bộ
from document_parser import extract_text_from_file
from database import save_dossier, get_all_dossiers
from exporter import generate_bid_docx
from ai_engine import extract_rfp_with_gemini, chat_with_assistant, GEMINI_API_KEY

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thiên Minh AI — Thế Hệ Chào Giá Tiếp Theo",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. HỆ THỐNG DESIGN & HIỆU ỨNG CHUYỂN ĐỘNG (LẤY CẢM HỨNG TỪ 3 TEMPLATES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Nền lưới kiến trúc nhẹ nhàng (Template 3) + Canvas sáng dịu (Template 1) */
    .stApp {
        background-color: #f6f8fb;
        background-image: linear-gradient(to right, rgba(15, 23, 42, 0.028) 1px, transparent 1px);
        background-size: 96px 100%;
    }
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
        max-width: 1420px;
    }

    /* Animation keyframes */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.35); }
        50%      { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    }

    /* Hero Banner kết hợp Dark AI (Template 2) + Emerald Accent (Template 1) */
    .tm-hero {
        background: radial-gradient(circle at 88% 20%, rgba(236, 72, 153, 0.22), transparent 36%),
                    radial-gradient(circle at 72% 85%, rgba(56, 189, 248, 0.20), transparent 40%),
                    linear-gradient(125deg, #070b14 0%, #0f172a 55%, #064e3b 100%);
        border-radius: 18px;
        padding: 22px 30px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 14px 36px rgba(7, 11, 20, 0.18);
        margin-bottom: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        animation: fadeSlideUp 0.45s ease-out;
        transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.3s ease;
    }
    .tm-hero:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 42px rgba(7, 11, 20, 0.24);
    }
    .tm-eyebrow {
        font-size: 0.72rem;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .tm-hero-title {
        margin: 0;
        font-size: 1.62rem;
        font-weight: 800;
        letter-spacing: -0.4px;
        line-height: 1.2;
    }
    .grad-cyan-pink {
        background: linear-gradient(90deg, #38bdf8 0%, #2dd4bf 45%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .tm-hero-sub {
        margin: 6px 0 0 0;
        font-size: 0.88rem;
        color: #cbd5e1;
        font-weight: 400;
    }
    .tm-status-group {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .tm-pill-glow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #e0f2fe;
        transition: all 0.25s ease;
    }
    .tm-pill-glow:hover {
        background: rgba(56, 189, 248, 0.16);
        border-color: #f472b6;
        transform: scale(1.03);
    }
    .dot-live {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        animation: pulseGlow 2s infinite;
    }

    /* Thanh Stepper 4 bước mượt mà */
    .stepper-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 16px;
    }
    .step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.84rem;
        font-weight: 600;
        color: #64748b;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
        transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
        cursor: default;
    }
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        border-color: #cbd5e1;
    }
    .step-card.active {
        background: linear-gradient(135deg, #ecfdf5 0%, #eff6ff 100%);
        border-color: #10b981;
        color: #065f46;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.14);
    }
    .step-card.done {
        background: #ffffff;
        border-color: #10b981;
        border-left: 4px solid #10b981;
        color: #047857;
    }
    .step-card.warn {
        background: #fef2f2;
        border-color: #f43f5e;
        border-left: 4px solid #e11d48;
        color: #9f1239;
    }
    .step-num {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #f1f5f9;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 800;
        flex-shrink: 0;
    }
    .step-card.active .step-num { background: #10b981; color: white; }
    .step-card.done .step-num   { background: #d1fae5; color: #047857; }
    .step-card.warn .step-num   { background: #ffe4e6; color: #be123c; }

    /* KPI Cards kiểu Fintech (Template 1) với thanh màu bên dưới + Sparkline + Hover Lift */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 12px 0 18px 0;
        animation: fadeSlideUp 0.4s ease-out;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e8eef5;
        border-radius: 14px;
        padding: 14px 16px 12px 16px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        transition: all 0.28s cubic-bezier(0.22, 1, 0.36, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 28px rgba(15, 23, 42, 0.09);
        border-color: #cbd5e1;
    }
    .kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.76rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .kpi-val {
        font-size: 1.26rem;
        font-weight: 800;
        color: #0f172a;
        margin: 6px 0 4px 0;
        letter-spacing: -0.3px;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .kpi-bar {
        height: 4px;
        border-radius: 99px;
        width: 100%;
    }
    .bar-emerald { background: linear-gradient(90deg, #10b981, #34d399); }
    .bar-indigo  { background: linear-gradient(90deg, #6366f1, #818cf8); }
    .bar-amber   { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .bar-cyan    { background: linear-gradient(90deg, #06b6d4, #38bdf8); }

    /* Scenario Gradient Badges (Cảm hứng từ dãy thẻ Accounts & Cards ở Template 1) */
    .scenario-hint {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 10px;
    }
    .sc-card {
        border-radius: 12px;
        padding: 12px 14px;
        color: #0f172a;
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .sc-card:hover {
        transform: translateY(-3px) scale(1.015);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.1);
    }
    .sc-mint   { background: linear-gradient(135deg, #d1fae5 0%, #ecfeff 100%); }
    .sc-amber  { background: linear-gradient(135deg, #fef3c7 0%, #ffedd5 100%); }
    .sc-rose   { background: linear-gradient(135deg, #fce7f3 0%, #e0e7ff 100%); }
    .sc-title  { font-size: 0.82rem; font-weight: 800; margin-bottom: 2px; }
    .sc-desc   { font-size: 0.74rem; color: #334155; }

    /* Hộp Giá tổng nổi bật */
    .price-spotlight {
        background: linear-gradient(135deg, #064e3b 0%, #0f766e 60%, #0284c7 100%);
        border-radius: 14px;
        padding: 18px 22px;
        color: white;
        margin: 12px 0;
        box-shadow: 0 10px 24px rgba(6, 78, 59, 0.22);
        transition: transform 0.25s ease;
    }
    .price-spotlight:hover {
        transform: translateY(-2px);
    }
    .price-spotlight .lbl { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.8px; color: #a7f3d0; font-weight: 700; }
    .price-spotlight .num { font-size: 1.75rem; font-weight: 800; margin-top: 4px; color: #ffffff; }

    /* Hiệu ứng di chuột cho tất cả Buttons & Tabs */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.24s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px rgba(16, 185, 129, 0.22) !important;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border: none !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 10px 22px rgba(5, 150, 105, 0.32) !important;
    }

    /* Tabs mượt mà */
    button[data-baseweb="tab"] {
        border-radius: 10px 10px 0 0 !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease, color 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: rgba(16, 185, 129, 0.08) !important;
        color: #059669 !important;
    }

    /* Chatbot Header sang trọng */
    .chat-header-modern {
        background: radial-gradient(circle at 90% 20%, rgba(236, 72, 153, 0.25), transparent 45%),
                    linear-gradient(120deg, #0b1120 0%, #1e293b 100%);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 14px 14px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .chat-badge {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(16, 185, 129, 0.5);
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
    }

    /* Expander card sạch sẽ */
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.03);
        transition: box-shadow 0.25s ease;
    }
    div[data-testid="stExpander"]:hover {
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD DỮ LIỆU ---
@st.cache_data
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "business_rules.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
catalog = config.get("catalog", [])
approval_rules = config.get("approval_rules", {})
ops_capacity = config.get("operations_capacity", {"total_capacity_mandays": 110, "booked_mandays_current_month": 68})
rem_mandays = ops_capacity["total_capacity_mandays"] - ops_capacity["booked_mandays_current_month"]

# --- 4. KỊCH BẢN MẪU ---
SCENARIOS = {
    "k1": {
        "label": "🟢 Kịch bản 1: Chuẩn (CK 4%)",
        "client": "Ngân hàng TMCP Sài Gòn (SCB)",
        "text": """Kính gửi Công ty Thiên Minh,
Chúng tôi cần mua sắm thiết bị mở rộng chi nhánh:
- 01 Thiết bị Firewall Fortinet FortiGate 100F
- 04 Switch Cisco Catalyst 1000 24-Port PoE+
- Dịch vụ lắp đặt và cấu hình hoàn thiện
Thời hạn bàn giao: 10 ngày làm việc. Đề nghị chiết khấu 4%."""
    },
    "k2": {
        "label": "🟡 Kịch bản 2: Thiếu thông tin",
        "client": "Công ty TNHH Xây dựng Phúc Hưng",
        "text": """Chào Thiên Minh,
Bên mình cần lắp mạng cho tòa nhà 3 tầng mới hoàn thiện.
Cần switch mạng và cục phát wifi chịu tải tốt, hỗ trợ cổng Gigabit.
Báo giá sớm giúp mình phương án tối ưu."""
    },
    "k3": {
        "label": "🔴 Kịch bản 3: Vượt quyền (CK 9% + SLA 2h)",
        "client": "Tập đoàn Bán lẻ Vinamart",
        "text": """Gửi phòng Dự án Thiên Minh,
Yêu cầu chào thầu hạ tầng mạng trung tâm dữ liệu:
1. 02 Switch Cisco Catalyst 9300X 24-Port 10G/25G quang Core
2. 04 Switch Cisco Catalyst 9300 48-Port PoE+ Layer 3
3. 01 Firewall FortiGate 100F
4. Bảo trì: Cam kết SLA 24/7 có mặt trong vòng 2 giờ (bắt buộc)
5. Hoàn thành trong 12 ngày làm việc. Chiết khấu đề nghị: 9%."""
    }
}

# --- 5. SESSION STATE ---
if "rfp_client" not in st.session_state:
    st.session_state.rfp_client = SCENARIOS["k3"]["client"]
if "rfp_text" not in st.session_state:
    st.session_state.rfp_text = SCENARIOS["k3"]["text"]
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "approval_status" not in st.session_state:
    st.session_state.approval_status = "PENDING"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Xin chào! Tôi là **Trợ lý AI Thiên Minh** 🤖.\n\nHãy chọn một mẫu kịch bản hoặc tải file RFP bên trái rồi nhấn **Phân tích**, hoặc hỏi tôi bất cứ điều gì về tồn kho, giá và quy định duyệt!"
        }
    ]

# --- 6. HERO BANNER (THẾ HỆ TIẾP THEO) ---
ai_status = "Gemini AI Sẵn sàng" if GEMINI_API_KEY else "Smart Rule Engine"
st.markdown(f"""
<div class="tm-hero">
    <div>
        <div class="tm-eyebrow">NỀN TẢNG ĐÁNH GIÁ CHÀO GIÁ B2B • CÔNG TY THIÊN MINH</div>
        <h1 class="tm-hero-title">TRỢ LÝ AI <span class="grad-cyan-pink">THẾ HỆ TIẾP THEO</span></h1>
        <p class="tm-hero-sub">Bóc tách hồ sơ RFP tự động • Chống báo sai cấu hình &amp; tiến độ • Thẩm định đa cấp &amp; Chatbot đồng hành</p>
    </div>
    <div class="tm-status-group">
        <div class="tm-pill-glow"><span class="dot-live"></span> {ai_status}</div>
        <div class="tm-pill-glow">➔ Quỹ kỹ thuật: {rem_mandays} công trống</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 7. SIDEBAR GỌN NHẸ ---
with st.sidebar:
    st.markdown("### 👤 Vai trò thao tác")
    user_role = st.selectbox(
        "Vai trò",
        ["Nhân viên Kinh doanh (Sales)", "Trưởng phòng Kinh doanh (Approver)", "Kỹ thuật & Vận hành", "Ban Giám đốc"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("### 📅 Năng lực Kỹ thuật tháng")
    st.progress(ops_capacity["booked_mandays_current_month"] / ops_capacity["total_capacity_mandays"])
    st.caption(f"Đã đặt {ops_capacity['booked_mandays_current_month']}/{ops_capacity['total_capacity_mandays']} ngày công (**{rem_mandays} công trống**)")
    st.markdown("---")
    st.markdown("### 🛡️ Ma trận Phê duyệt")
    st.markdown("""
    - 🟢 **Sales:** CK `≤ 5%`, đủ hàng, SLA chuẩn
    - 🟡 **Trưởng phòng:** CK `5% – 10%` hoặc SLA `2h`
    - 🔴 **Ban Giám đốc:** CK `> 10%`, ngoài danh mục, trễ lịch
    """)
    if st.button("🔄 Làm mới toàn bộ", width="stretch"):
        st.session_state.parsed_data = None
        st.session_state.approval_status = "PENDING"
        st.rerun()

# --- 8. TABS ĐIỀU HƯỚNG CHÍNH ---
tab_main, tab_history, tab_catalog = st.tabs([
    "💼 Không gian Xử lý & Chatbot AI",
    "📚 Lịch sử Hồ sơ Đã lưu",
    "📦 Danh mục Thiết bị & Tồn kho"
])

# =========================================================================
# TAB 2: LỊCH SỬ HỒ SƠ
# =========================================================================
with tab_history:
    records = get_all_dossiers()
    if records:
        df_h = pd.DataFrame(records)[[
            "dossier_code", "client_name", "deadline_days",
            "discount_requested", "final_bid_price", "approval_level", "status", "created_at"
        ]].rename(columns={
            "dossier_code": "Mã Hồ sơ", "client_name": "Khách hàng", "deadline_days": "Hạn (ngày)",
            "discount_requested": "CK (%)", "final_bid_price": "Giá chào (VNĐ)",
            "approval_level": "Cấp duyệt", "status": "Trạng thái", "created_at": "Thời gian tạo"
        })
        st.dataframe(df_h, width="stretch", hide_index=True)
    else:
        st.info("Chưa có hồ sơ nào được lưu. Sau khi thẩm định xong, bạn hãy bấm **Lưu vào Lịch sử** để theo dõi tại đây.")

# =========================================================================
# TAB 3: DANH MỤC THIẾT BỊ & TỒN KHO
# =========================================================================
with tab_catalog:
    if catalog:
        df_cat = pd.DataFrame([{
            "Mã SKU": c["sku"], "Tên Thiết bị / Dịch vụ": c["name"], "Nhóm": c.get("category", ""),
            "Đơn giá (VNĐ)": f"{c['unit_price']:,.0f}", "Tồn kho": c["stock"], "Lead-time (ngày)": c["lead_time_days"]
        } for c in catalog])
        st.dataframe(df_cat, width="stretch", hide_index=True)

# =========================================================================
# TAB 1: KHÔNG GIAN 2 CỘT (TRÁI: QUY TRÌNH | PHẢI: CHATBOT COPILOT)
# =========================================================================
with tab_main:
    col_work, col_chat = st.columns([1.65, 1.0], gap="medium")
    chatbot_context = {}

    # ---------------------------------------------------------------------
    # CỘT TRÁI: QUY TRÌNH ĐÁNH GIÁ
    # ---------------------------------------------------------------------
    with col_work:
        p = st.session_state.parsed_data

        # Tính trạng thái cho 4 bước Stepper
        s1 = "done" if p else "active"
        if not p:
            s2 = s3 = s4 = ""
        elif not p["is_sufficient"]:
            s2, s3, s4 = "warn", "", ""
        else:
            s2 = "done"
            s3 = "done" if st.session_state.approval_status in ["APPROVED", "AUTO_APPROVED"] else ("warn" if st.session_state.approval_status == "REJECTED" else "active")
            s4 = "active" if st.session_state.approval_status in ["APPROVED", "AUTO_APPROVED"] else ""

        st.markdown(f"""
        <div class="stepper-grid">
            <div class="step-card {s1}"><span class="step-num">1</span> Tiếp nhận RFP</div>
            <div class="step-card {s2}"><span class="step-num">2</span> Kiểm tra &amp; Kỹ thuật</div>
            <div class="step-card {s3}"><span class="step-num">3</span> Giá &amp; Thẩm quyền</div>
            <div class="step-card {s4}"><span class="step-num">4</span> Duyệt cuối &amp; Xuất</div>
        </div>
        """, unsafe_allow_html=True)

        # Khung nhập yêu cầu với dải thẻ Pastel kiểu Template 1
        with st.expander("📥 Bước 1: Chọn Kịch bản hoặc Tải Hồ sơ Yêu cầu (RFP/RFQ)", expanded=(p is None)):
            st.markdown("""
            <div class="scenario-hint">
                <div class="sc-card sc-mint">
                    <div class="sc-title">🟢 Kịch bản 1 — Chuẩn</div>
                    <div class="sc-desc">Đủ thông tin, CK 4% → Sales tự quyết &amp; xuất báo giá ngay.</div>
                </div>
                <div class="sc-card sc-amber">
                    <div class="sc-title">🟡 Kịch bản 2 — Thiếu dữ liệu</div>
                    <div class="sc-desc">Mơ hồ cấu hình/hạn chót → AI chặn lại &amp; tạo thư RFI.</div>
                </div>
                <div class="sc-card sc-rose">
                    <div class="sc-title">🔴 Kịch bản 3 — Vượt quyền</div>
                    <div class="sc-desc">CK 9% + SLA 2h → Chuyển Trưởng phòng phê duyệt.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            qb1, qb2, qb3, qb4 = st.columns(4)
            if qb1.button(SCENARIOS["k1"]["label"], width="stretch"):
                st.session_state.rfp_client = SCENARIOS["k1"]["client"]
                st.session_state.rfp_text = SCENARIOS["k1"]["text"]
                st.session_state.parsed_data = None
                st.rerun()
            if qb2.button(SCENARIOS["k2"]["label"], width="stretch"):
                st.session_state.rfp_client = SCENARIOS["k2"]["client"]
                st.session_state.rfp_text = SCENARIOS["k2"]["text"]
                st.session_state.parsed_data = None
                st.rerun()
            if qb3.button(SCENARIOS["k3"]["label"], width="stretch"):
                st.session_state.rfp_client = SCENARIOS["k3"]["client"]
                st.session_state.rfp_text = SCENARIOS["k3"]["text"]
                st.session_state.parsed_data = None
                st.rerun()
            if qb4.button("✍️ Nhập trống mới", width="stretch"):
                st.session_state.rfp_client = ""
                st.session_state.rfp_text = ""
                st.session_state.parsed_data = None
                st.rerun()

            in_type = st.radio("Nguồn nhập:", ["Dán văn bản", "Tải file (PDF, Word, Excel)"], horizontal=True, label_visibility="collapsed")
            client_in = st.text_input("Tên Khách hàng / Doanh nghiệp:", value=st.session_state.rfp_client, placeholder="Ví dụ: Công ty Cổ phần ABC")

            if in_type == "Dán văn bản":
                text_in = st.text_area("Nội dung Email / Yêu cầu kỹ thuật:", value=st.session_state.rfp_text, height=145, placeholder="Dán yêu cầu của khách hàng vào đây...")
            else:
                up_file = st.file_uploader("Chọn file RFP:", type=["pdf", "docx", "doc", "xlsx", "txt"])
                text_in = extract_text_from_file(up_file.read(), up_file.name) if up_file else ""
                if text_in:
                    st.text_area("Nội dung đọc từ file:", value=text_in[:1000], height=120)

            if st.button("🚀 PHÂN TÍCH YÊU CẦU BẰNG AI", type="primary", width="stretch", disabled=(not text_in.strip())):
                with st.spinner("🤖 AI đang bóc tách yêu cầu, đối chiếu kho và tính giá..."):
                    st.session_state.rfp_client = client_in or "Khách hàng Doanh nghiệp"
                    st.session_state.rfp_text = text_in
                    extracted = extract_rfp_with_gemini(text_in, catalog)
                    st.session_state.parsed_data = {
                        "client": st.session_state.rfp_client,
                        "project_name": "Gói thiết bị mạng & dịch vụ triển khai",
                        "is_sufficient": extracted.get("is_sufficient", False),
                        "missing_fields": extracted.get("missing_fields", []),
                        "items": extracted.get("items", []),
                        "discount_requested_pct": float(extracted.get("discount_requested_pct", 0.0)),
                        "deadline_days": int(extracted.get("deadline_days", 10)),
                        "sla_requirement": extracted.get("sla_requirement", "8x5 Tiêu chuẩn NBD")
                    }
                    st.session_state.approval_status = "PENDING"
                    st.rerun()

        # HIỂN THỊ KẾT QUẢ PHÂN TÍCH
        if st.session_state.parsed_data:
            p = st.session_state.parsed_data

            # NHÁNH A: THIẾU THÔNG TIN -> RFI
            if not p["is_sufficient"]:
                chatbot_context = p
                st.error("⛔ **Hồ sơ chưa đủ thông tin cốt lõi — Tạm dừng báo giá!**")
                st.markdown("**Các thông tin bắt buộc còn thiếu:** " + ", ".join([f"`{m}`" for m in p["missing_fields"]]))
                draft_rfi = f"""Kính gửi Quý Khách hàng ({p['client']}),

Công ty Cổ phần Công nghệ Thiên Minh trân trọng cảm ơn Quý công ty đã gửi yêu cầu hợp tác.
Để đảm bảo tư vấn đúng giải pháp kỹ thuật và lập bảng chào giá chính xác nhất, kính đề nghị Quý khách bổ sung:
{chr(10).join([f'  - {m}' for m in p['missing_fields']])}

Ngay khi nhận được thông tin bổ sung, Thiên Minh sẽ hoàn thiện và gửi bản chào giá trong vòng 2 giờ làm việc.

Trân trọng,
Phòng Kinh doanh - Công ty Thiên Minh"""
                st.text_area("✉️ Thư nháp hỏi làm rõ (RFI) gửi khách hàng:", value=draft_rfi, height=175)
                if st.button("📤 Lưu trạng thái 'Chờ khách bổ sung'", type="primary"):
                    code = save_dossier({
                        "client_name": p["client"], "project_name": p["project_name"],
                        "deadline_days": 0, "discount_requested": 0, "total_list_price": 0,
                        "final_bid_price": 0, "approval_level": "Chưa xác định",
                        "status": "PENDING_CLARIFICATION", "compliance_summary": {"missing": p["missing_fields"]},
                        "pricing_details": {}
                    })
                    st.success(f"✅ Đã lưu hồ sơ **{code}** vào hệ thống theo dõi.")

            # NHÁNH B: ĐỦ THÔNG TIN -> TÍNH TOÁN & HIỂN THỊ KPI CARDS KIỂU TEMPLATE 1
            else:
                feasibility_rows = []
                total_mandays = 0.0
                max_lead = 0

                for it in p["items"]:
                    sku = it.get("sku", "")
                    cat = next((c for c in catalog if c["sku"] == sku), None)
                    qty = int(it.get("qty", 1))
                    if cat:
                        stock = cat["stock"]
                        lead = cat["lead_time_days"] + (0 if stock >= qty else 7)
                        max_lead = max(max_lead, lead)
                        feasibility_rows.append({
                            "Mã SKU": sku,
                            "Tên Hạng mục": cat["name"],
                            "SL": qty,
                            "Tồn kho": stock,
                            "Đơn giá (VNĐ)": cat["unit_price"],
                            "Thành tiền (VNĐ)": cat["unit_price"] * qty,
                            "Kho": "✅ Sẵn" if stock >= qty else f"⚠️ Thiếu ({stock}/{qty})",
                            "Giao": f"{lead} ngày"
                        })
                        total_mandays += float(it.get("mandays", 0))
                    else:
                        max_lead = max(max_lead, 14)
                        feasibility_rows.append({
                            "Mã SKU": "OUT_OF_CATALOG",
                            "Tên Hạng mục": it.get("name", "Thiết bị ngoài danh mục"),
                            "SL": qty,
                            "Tồn kho": 0,
                            "Đơn giá (VNĐ)": 20000000,
                            "Thành tiền (VNĐ)": 20000000 * qty,
                            "Kho": "🚨 Ngoài DM",
                            "Giao": "14 ngày"
                        })
                        total_mandays += float(it.get("mandays", 2.0))

                sched_ok = (total_mandays <= rem_mandays) and (max_lead <= p["deadline_days"])
                subtotal = sum(r["Thành tiền (VNĐ)"] for r in feasibility_rows)
                sla_fee = 18000000 if "2h" in p["sla_requirement"] else 0
                total_list_price = subtotal + sla_fee
                discount_pct = p["discount_requested_pct"]
                discount_amount = total_list_price * discount_pct / 100
                final_price = total_list_price - discount_amount

                escalations = []
                approval_level = "Sales tự quyết"
                if discount_pct > approval_rules["sales_manager"]["max_discount_pct"]:
                    approval_level = "Ban Giám đốc duyệt"
                    escalations.append(f"Chiết khấu {discount_pct}% vượt trần Trưởng phòng (> 10%)")
                elif discount_pct > approval_rules["sales_rep"]["max_discount_pct"]:
                    approval_level = "Trưởng phòng KD duyệt"
                    escalations.append(f"Chiết khấu {discount_pct}% vượt quyền Sales (≤ 5%)")
                if any(r["Mã SKU"] == "OUT_OF_CATALOG" for r in feasibility_rows):
                    approval_level = "Ban Giám đốc duyệt"
                    escalations.append("Có thiết bị ngoài danh mục chuẩn")
                if "2h" in p["sla_requirement"]:
                    if approval_level != "Ban Giám đốc duyệt":
                        approval_level = "Trưởng phòng KD duyệt"
                    escalations.append("Yêu cầu SLA khẩn cấp 24/7/2h")
                if not sched_ok:
                    approval_level = "Ban Giám đốc duyệt"
                    escalations.append("Rủi ro chậm tiến độ hoặc thiếu công kỹ sư")

                requires_approval = len(escalations) > 0
                if not requires_approval:
                    st.session_state.approval_status = "AUTO_APPROVED"

                chatbot_context = {
                    **p,
                    "max_lead_days": max_lead,
                    "total_mandays": total_mandays,
                    "sched_ok": sched_ok,
                    "total_list_price": total_list_price,
                    "final_price": final_price,
                    "approval_level": approval_level,
                    "escalations": escalations,
                    "approval_status": st.session_state.approval_status
                }

                # 4 KPI Cards kèm thanh màu sắc hài hòa (Template 1)
                spark_green = '<svg width="56" height="20" viewBox="0 0 56 20"><path d="M2 16 Q 14 4, 24 12 T 42 8 T 54 3" fill="none" stroke="#10b981" stroke-width="2.2" stroke-linecap="round"/></svg>'
                spark_indigo = '<svg width="56" height="20" viewBox="0 0 56 20"><path d="M2 14 Q 16 14, 26 8 T 44 10 T 54 5" fill="none" stroke="#6366f1" stroke-width="2.2" stroke-linecap="round"/></svg>'
                spark_amber = '<svg width="56" height="20" viewBox="0 0 56 20"><path d="M2 12 Q 16 18, 28 9 T 44 13 T 54 6" fill="none" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round"/></svg>'
                spark_cyan = '<svg width="56" height="20" viewBox="0 0 56 20"><path d="M2 15 Q 15 8, 28 11 T 45 5 T 54 4" fill="none" stroke="#06b6d4" stroke-width="2.2" stroke-linecap="round"/></svg>'

                st.markdown(f"""
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-top"><span>Giá chào dự kiến</span>{spark_green}</div>
                        <div class="kpi-val">{final_price/1e6:,.1f} triệu</div>
                        <div class="kpi-sub" style="color:#059669;">Chiết khấu {discount_pct}%</div>
                        <div class="kpi-bar bar-emerald"></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-top"><span>Tiến độ giao hàng</span>{spark_indigo}</div>
                        <div class="kpi-val">{max_lead} ngày</div>
                        <div class="kpi-sub" style="color:#4f46e5;">Hạn chót: {p['deadline_days']} ngày</div>
                        <div class="kpi-bar bar-indigo"></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-top"><span>Công kỹ thuật</span>{spark_amber}</div>
                        <div class="kpi-val">{total_mandays:.1f} công</div>
                        <div class="kpi-sub" style="color:#d97706;">Còn trống: {rem_mandays} công</div>
                        <div class="kpi-bar bar-amber"></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-top"><span>Thẩm quyền duyệt</span>{spark_cyan}</div>
                        <div class="kpi-val" style="font-size:1.05rem; padding-top:4px;">{approval_level}</div>
                        <div class="kpi-sub" style="color:#0891b2;">{"Tự động hợp lệ" if not requires_approval else f"{len(escalations)} cảnh báo"}</div>
                        <div class="kpi-bar bar-cyan"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 4 Tabs kết quả siêu gọn
                rt1, rt2, rt3, rt4 = st.tabs([
                    "📋 1. Tóm tắt & Đáp ứng",
                    "🔧 2. Kho & Lịch Kỹ sư",
                    "✍️ 3. Duyệt Thẩm quyền",
                    "📄 4. Xuất Báo giá (.DOCX)"
                ])

                with rt1:
                    st.markdown(f"**Khách hàng:** `{p['client']}` &nbsp;•&nbsp; **SLA:** `{p['sla_requirement']}`")
                    comp_data = [{
                        "Hạng mục": it.get("name", "Thiết bị"),
                        "Số lượng": it.get("qty", 1),
                        "Đáp ứng (Compliance)": "⚠️ PARTIAL" if it.get("sku") == "OUT_OF_CATALOG" else "✅ COMPLY",
                        "Đánh giá Rủi ro": "Nhập từ đối tác" if it.get("sku") == "OUT_OF_CATALOG" else "Đạt chuẩn catalog"
                    } for it in p["items"]]
                    comp_data.append({
                        "Hạng mục": f"Dịch vụ Bảo trì ({p['sla_requirement']})",
                        "Số lượng": 1,
                        "Đáp ứng (Compliance)": "✅ COMPLY" if "8x5" in p["sla_requirement"] else "⚠️ PARTIAL",
                        "Đánh giá Rủi ro": "Chuẩn công ty" if "8x5" in p["sla_requirement"] else "Đã tính 18tr phụ phí"
                    })
                    st.dataframe(pd.DataFrame(comp_data), width="stretch", hide_index=True)

                with rt2:
                    st.dataframe(
                        pd.DataFrame(feasibility_rows).style.format({"Đơn giá (VNĐ)": "{:,.0f}", "Thành tiền (VNĐ)": "{:,.0f}"}),
                        width="stretch",
                        hide_index=True
                    )
                    if sched_ok:
                        st.success(f"✅ Lịch trình hoàn toàn khả thi ({max_lead} ≤ {p['deadline_days']} ngày; cần {total_mandays:.1f} công ≤ {rem_mandays} công trống).")
                    else:
                        st.error("⚠️ Tiến độ hoặc nhân lực có nguy cơ trễ hẹn! Hãy hỏi Trợ lý AI bên phải để có phương án đàm phán.")

                with rt3:
                    st.markdown(f"""
                    - Giá thiết bị & dịch vụ niêm yết: **{subtotal:,.0f} VNĐ**
                    - Phụ phí SLA ({p['sla_requirement']}): **{sla_fee:,.0f} VNĐ**
                    - Chiết khấu ({discount_pct}%): **- {discount_amount:,.0f} VNĐ**
                    """)
                    st.markdown(f"""
                    <div class="price-spotlight">
                        <div class="lbl">💰 Giá chào thầu sau chiết khấu (Chưa VAT)</div>
                        <div class="num">{final_price:,.0f} VNĐ</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if requires_approval:
                        st.warning(f"⚠️ **Cần {approval_level}** vì:\n" + "\n".join([f"- {e}" for e in escalations]))
                        note_in = st.text_input("Ghi chú phê duyệt:", value="Đồng ý phương án & chiết khấu.")
                        b_ok, b_no = st.columns(2)
                        if b_ok.button("✅ PHÊ DUYỆT NGAY", type="primary", width="stretch"):
                            st.session_state.approval_status = "APPROVED"
                            st.rerun()
                        if b_no.button("❌ TỪ CHỐI", width="stretch"):
                            st.session_state.approval_status = "REJECTED"
                            st.rerun()

                        if st.session_state.approval_status == "APPROVED":
                            st.success("✅ Đã được **PHÊ DUYỆT**! Chuyển sang tab **4. Xuất Báo giá** để tải file.")
                        elif st.session_state.approval_status == "REJECTED":
                            st.error("❌ Đã bị **TỪ CHỐI**.")
                    else:
                        st.success("✅ Hợp lệ trong thẩm quyền của Sales — sẵn sàng xuất báo giá ở Tab 4!")

                with rt4:
                    if st.session_state.approval_status not in ["APPROVED", "AUTO_APPROVED"]:
                        st.warning("⏳ Vui lòng hoàn tất bước **Phê duyệt Thẩm quyền (Tab 3)** trước khi xuất bản chào giá chính thức.")
                    else:
                        st.markdown("#### ✔️ Kiểm tra cuối trước khi gửi (HITL 3 Bộ phận)")
                        c1, c2, c3 = st.columns(3)
                        ck_kd = c1.checkbox("Kinh doanh OK", value=True)
                        ck_kt = c2.checkbox("Kỹ thuật OK", value=True)
                        ck_vh = c3.checkbox("Vận hành OK", value=True)

                        if ck_kd and ck_kt and ck_vh:
                            export_pricing_rows = [{
                                "Tên Hạng mục": r["Tên Hạng mục"],
                                "SL Yêu cầu": r["SL"],
                                "Đơn giá niêm yết (VNĐ)": r["Đơn giá (VNĐ)"],
                                "Thành tiền (VNĐ)": r["Thành tiền (VNĐ)"]
                            } for r in feasibility_rows]

                            export_data = {
                                "client": p["client"],
                                "project_name": p["project_name"],
                                "compliance_matrix": comp_data,
                                "pricing_rows": export_pricing_rows,
                                "total_list_price": total_list_price,
                                "discount_pct": discount_pct,
                                "discount_amount": discount_amount,
                                "final_price": final_price,
                                "deadline_days": p["deadline_days"],
                                "sla_requirement": p["sla_requirement"]
                            }
                            docx_file = generate_bid_docx(export_data)

                            d1, d2 = st.columns(2)
                            d1.download_button(
                                label="📄 TẢI BẢN CHÀO GIÁ (.DOCX)",
                                data=docx_file,
                                file_name=f"Bao_Gia_ThienMinh_{p['client'].replace(' ', '_')}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                type="primary",
                                width="stretch"
                            )
                            if d2.button("💾 LƯU VÀO LỊCH SỬ", width="stretch"):
                                code = save_dossier({
                                    "client_name": p["client"],
                                    "project_name": p["project_name"],
                                    "deadline_days": p["deadline_days"],
                                    "discount_requested": discount_pct,
                                    "total_list_price": total_list_price,
                                    "final_bid_price": final_price,
                                    "approval_level": approval_level,
                                    "status": "ISSUED",
                                    "compliance_summary": comp_data,
                                    "pricing_details": export_data,
                                    "approval_notes": "Đã thẩm định 3 bên"
                                })
                                st.balloons()
                                st.success(f"🎉 Đã lưu thành công mã **{code}**!")

    # ---------------------------------------------------------------------
    # CỘT PHẢI: TRỢ LÝ AI CHATBOT TÍCH HỢP
    # ---------------------------------------------------------------------
    with col_chat:
        st.markdown("""
        <div class="chat-header-modern">
            <div>
                <div style="font-weight:700; font-size:0.96rem;">💬 Trợ lý AI Thiên Minh</div>
                <div style="font-size:0.74rem; color:#94a3b8;">Đồng hành thẩm định &amp; tư vấn báo giá</div>
            </div>
            <span class="chat-badge">● LIVE COPILOT</span>
        </div>
        """, unsafe_allow_html=True)

        chat_box = st.container(height=410, border=True)
        with chat_box:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        st.caption("⚡ Hỏi nhanh 1-click:")
        qc1, qc2 = st.columns(2)
        quick_q = None
        if qc1.button("📌 Tóm tắt rủi ro", width="stretch"):
            quick_q = "Tóm tắt các rủi ro và điểm cần lưu ý của hồ sơ đang mở?"
        if qc2.button("🤝 Gợi ý đàm phán", width="stretch"):
            quick_q = "Gợi ý cách đàm phán chiết khấu và tiến độ với khách hàng cho hồ sơ này?"

        qc3, qc4 = st.columns(2)
        if qc3.button("📦 Check giá & kho", width="stretch"):
            quick_q = "Kiểm tra giúp tôi danh mục giá và tồn kho hiện có?"
        if qc4.button("🛡️ Quy định duyệt", width="stretch"):
            quick_q = "Giải thích quy định chuyển duyệt chiết khấu của Thiên Minh?"

        with st.form(key="chatbot_form", clear_on_submit=True):
            fc1, fc2 = st.columns([4, 1.35])
            user_q = fc1.text_input("Nhập câu hỏi...", placeholder="Hỏi AI về hồ sơ, giá, tồn kho...", label_visibility="collapsed")
            send_clicked = fc2.form_submit_button("Gửi ➤", type="primary", width="stretch")

        final_query = quick_q or (user_q.strip() if send_clicked and user_q.strip() else None)

        if final_query:
            st.session_state.chat_messages.append({"role": "user", "content": final_query})
            reply = chat_with_assistant(
                final_query,
                st.session_state.chat_messages,
                chatbot_context,
                config
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()

        if st.button("🧹 Xóa lịch sử chat", width="stretch"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()
