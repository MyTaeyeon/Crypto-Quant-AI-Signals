import re
import json
import concurrent.futures
from collections import Counter
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH PERPLEXITY API
# ==========================================
# Thay API Key Perplexity của bạn vào đây
PERPLEXITY_API_KEY = "YOUR_PERPLEXITY_API_KEY_HERE"

# Perplexity sử dụng cấu trúc client giống hệt OpenAI
client = OpenAI(
    api_key=PERPLEXITY_API_KEY, 
    base_url="https://api.perplexity.ai"
)

# Danh sách 4 đồng coin cần feed cho module trade
COINS = ["BTC", "ETH", "SOL", "BNB"]

# ==========================================
# 2. HÀM GỌI PERPLEXITY AI (ALL-IN-ONE)
# ==========================================
def get_single_perplexity_signal():
    """Hàm yêu cầu Perplexity tự Search web và tự phân tích Sentiment"""
    
    prompt = f"""
    Bạn là một bot giao dịch Crypto thuật toán siêu tốc.
    Nhiệm vụ của bạn là: HÃY TỰ TÌM KIẾM tin tức mới nhất ngay lúc này trên internet về 4 đồng coin: {COINS}.
    
    Dựa vào tin tức vừa tìm được, hãy chấm điểm tín hiệu:
    - 1 (Mua): Có tin tức vĩ mô cực tốt (Dòng tiền vào, cập nhật mạng lưới, quỹ lớn mua).
    - -1 (Bán): Có tin xấu (Hack, rớt mạng, SEC kiện cáo).
    - 0 (Giữ): Tin tức trung lập, nhiễu, hoặc không có tác động mạnh.
    
    QUY TẮC ĐẦU RA (TỐI QUAN TRỌNG):
    - CHỈ trả về duy nhất một mảng JSON 4 số nguyên. Ví dụ chuẩn: [1, 0, -1, 1]
    - Bắt buộc KHÔNG giải thích. KHÔNG trích dẫn nguồn kiểu [1][2]. KHÔNG dùng markdown. CHỈ CÓ MẢNG SỐ.
    """
    
    try:
        # Gọi model sonar-pro: model mạnh nhất của Perplexity về Real-time Web Search
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": "You are a highly strictly formatted JSON output bot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1 # Rất thấp để tránh AI sáng tạo linh tinh
        )
        
        raw_text = response.choices[0].message.content
        
        # Regex bọc lót: Bắt buộc trích xuất đúng mảng 4 số, loại bỏ mọi text rác nếu AI lỡ in ra
        match = re.search(r'\[\s*(-?[01])\s*,\s*(-?[01])\s*,\s*(-?[01])\s*,\s*(-?[01])\s*\]', raw_text)
        if match:
            return json.loads(match.group(0))
        else:
            print(f"[Cảnh báo] Perplexity sai format: {raw_text}")
            return [0, 0, 0, 0] # Fail-safe
            
    except Exception as e:
        print(f"[Lỗi API Perplexity]: {e}")
        return [0, 0, 0, 0]

# ==========================================
# 3. HÀM CHỐT SỐ ĐÔNG (MAJORITY VOTE ENSEMBLE)
# ==========================================
def get_final_trading_signals():
    """Chạy 3 luồng Perplexity song song để triệt tiêu lỗi Ảo giác (Hallucination)"""
    print("🌐 Đang kết nối Perplexity AI để Search và Phân tích (Chạy 3 luồng song song)...")
    results =[]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures =[executor.submit(get_single_perplexity_signal) for _ in range(3)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    print(f"-> Dữ liệu thô từ 3 Agent (Tránh ảo giác): {results}")
    
    # Tính Mode (Số xuất hiện nhiều nhất) cho từng coin
    final_signal =[]
    for i in range(len(COINS)):
        coin_signals = [res[i] for res in results]
        most_common = Counter(coin_signals).most_common(1)[0][0]
        final_signal.append(most_common)
        
    return final_signal

# ==========================================
# 4. CHẠY THỰC TẾ
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 BẮT ĐẦU CHẠY MODULE PERPLEXITY AI SIGNALS 🚀")
    print("=" * 50)
    
    final_array = get_final_trading_signals()
    
    print("\n" + "=" * 50)
    print("🎯 DỮ LIỆU CUỐI CÙNG SẠCH 100% ĐỂ FEED CHO DEV TRADE 🎯")
    print(f"Tài sản:   {COINS}")
    print(f"Tín hiệu:  {final_array}")
    print("=" * 50)