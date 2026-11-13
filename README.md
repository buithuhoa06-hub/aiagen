# HỆ THỐNG AI AGENT ĐÁNH GIÁ CHÀO GIÁ DỰ ÁN - THIÊN MINH COMPANY

Hệ thống được xây dựng bám sát 100% sơ đồ quy trình nghiệp vụ:
1. **Tiếp nhận RFP/RFQ**
2. **[AI Agent 1] Trích xuất & Phân rã yêu cầu** (Bóc tách hạng mục, deadline, ngân sách, điều kiện bắt buộc)
   - Nếu thiếu thông tin -> Kinh doanh liên hệ KH yêu cầu bổ sung (AI sinh sẵn thư nháp RFI)
   - Nếu đủ thông tin -> Chuyển tiếp
3. **[AI Agent 2] Đối chiếu giải pháp, năng lực & lịch triển khai (Matching Feasibility)**
   - Kỹ thuật & Vận hành hỗ trợ dữ liệu (Catalog, Tồn kho, Mandays)
4. **[AI Agent 3] Tính toán giá đề xuất & Áp dụng chính sách chiết khấu**
   - Kiểm tra điều kiện vượt quyền (Chiết khấu cao, SLA khẩn cấp, thiết bị lạ) -> Chuyển duyệt Trưởng phòng / Ban Giám đốc
5. **Hợp nhất tài liệu**: Ma trận tuân thủ & Dự thảo bản chào giá
6. **HITL Thẩm định & Kiểm tra ranh giới dữ liệu** (KD + Kỹ thuật + Vận hành duyệt cuối) -> Xuất bản chào giá gửi khách hàng

---

## Hướng dẫn Chạy trên Localhost

### Cách 1: Chạy bằng file Click đúp (Khuyến nghị trên Windows)
- Click đúp vào file `run.bat` trong thư mục dự án `e:\Agent QTKD1`.

### Cách 2: Chạy từ Terminal / PowerShell
1. Mở PowerShell hoặc Command Prompt tại thư mục dự án:
   ```bash
   cd "e:\Agent QTKD1"
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Khởi động ứng dụng Streamlit:
   ```bash
   streamlit run app.py
   ```
4. Truy cập trình duyệt tại địa chỉ:
   ```
   http://localhost:8501
   ```

