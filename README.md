# Crypto Quant AI Signals

Một hệ thống tự động trích xuất tín hiệu giao dịch (Trading Signals) cho thị trường Crypto bằng việc kết hợp **Real-time Search** và **Large Language Models (LLMs)**. Hệ thống được thiết kế để chịu lỗi và đảm bảo cung cấp định dạng dữ liệu đầu ra chuẩn xác 100% cho các module giao dịch thuật toán ở phía sau.

## Vấn đề & Giải pháp
Các mô hình AI (LLM) thường gặp vấn đề **Ảo giác (Hallucination)** và **Thiếu nhất quán trong định dạng đầu ra (Non-deterministic output)**. Nếu đưa trực tiếp text của AI vào module giao dịch, hệ thống có thể bị crash.

Dự án này giải quyết triệt để bằng **Cơ chế phòng thủ 2 lớp (2-Layer Fail-Safe)**:
1. **Lớp 1 - Output Forcing (Regex):** Bắt buộc ép đầu ra của AI thành một mảng JSON chứa 4 giá trị số nguyên `[-1, 0, 1, -1]`. Nếu AI sinh ra văn bản thừa, Regex sẽ bóc tách và loại bỏ nội dung rác.
2. **Lớp 2 - Majority Vote Ensemble (Bầu chọn số đông):** Chạy song song (Concurrent) 3 luồng AI độc lập để đọc tin tức và phân tích. Tín hiệu cuối cùng được quyết định bằng thuật toán Mode (Số đông áp đảo), giúp loại bỏ hoàn toàn các nhận định sai lệch ngẫu nhiên của AI.

## 📊 Barem Tín Hiệu (Trading Rules)
Dự án phân tích 4 tài sản chính: `[BTC, ETH, SOL, BNB]`
* ` 1` (MUA): Tin tức vĩ mô cực tốt, dòng tiền lớn, cập nhật mạng lưới thành công.
* `-1` (BÁN): Tin tức xấu, FUD nặng, hack, rớt mạng, pháp lý (SEC).
* ` 0` (GIỮ): Tin tức trung lập, nhiễu loạn hoặc không rõ xu hướng.

## ⚙️ Cấu trúc dự án
Dự án hỗ trợ 2 kiến trúc chạy độc lập tùy thuộc vào API bạn đang có:
1. `gemini_tavily_agent.py`: Kiến trúc ghép (Microservices) dùng **Tavily API** để search và **Google Gemini API** (Miễn phí) để suy luận.
2. `perplexity_agent.py`: Kiến trúc All-in-one dùng **Perplexity API (sonar-pro)** tự động search và suy luận trong 1 bước.

## 🛠️ Cài đặt & Sử dụng

**1. Cài đặt thư viện:**
```bash
pip install google-generativeai tavily-python openai
