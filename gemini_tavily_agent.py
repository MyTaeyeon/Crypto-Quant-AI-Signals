import google.generativeai as genai
import re
import json
import concurrent.futures
from collections import Counter
from tavily import TavilyClient

# ==========================================
# 1. CẤU HÌNH API KEYS
# ==========================================
# Cấu hình Google Gemini (Model: gemini-1.5-flash hoặc gemini-2.0-flash nếu có)
GOOGLE_API_KEY = "YOUR_MODEL_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Cấu hình Tavily API (Lấy free tại app.tavily.com)
TAVILY_API_KEY = "TAVILY_API_KEY"

# Danh sách coin mục tiêu
COINS = ["BTC", "ETH", "SOL", "BNB"]

# ==========================================
# 2. HÀM TÌM KIẾM TIN TỨC VỚI TAVILY
# ==========================================
def get_tavily_news(coins):
    """Hàm tự động search tin tức mới nhất trong ngày cho các coin"""
    print(f"🔍 Đang gọi Tavily API cào tin nóng cho: {coins}...")
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Tạo câu query gộp để tiết kiệm lượt search
        query = f"Latest breaking crypto news today about: {', '.join(coins)}"
        
        # Thực hiện search
        response = tavily.search(query=query, search_depth="basic", max_results=6)
        
        # Gom kết quả lại thành 1 đoạn text chuẩn bị cho AI đọc
        news_context = ""
        for result in response.get('results',[]):
            news_context += f"- {result['title']}: {result['content']}\n"
            
        print("✅ Đã lấy xong tin tức từ Internet!")
        return news_context
        
    except Exception as e:
        print(f"❌ Lỗi Tavily Search: {e}")
        return "Không có dữ liệu tin tức mới."

# ==========================================
# 3. HÀM AI ĐỌC TIN VÀ PHÂN TÍCH
# ==========================================
def get_single_ai_evaluation(news_context):
    """Hàm gọi Google Gemini 1 lần để đọc tin và lấy tín hiệu"""
    prompt = f"""
    Bạn là một hệ thống phân tích Sentiment thị trường Crypto thuật toán.
    Nhiệm vụ: Đọc các tin tức sau và đưa ra tín hiệu cho 4 tài sản: {COINS}.
    
    TIN TỨC THỊ TRƯỜNG HIỆN TẠI (Dữ liệu từ Search):
    "{news_context}"
    
    BAREM CHẤM ĐIỂM (BẮT BUỘC TUÂN THỦ):
    - 1 (Mua): Có tin tức vĩ mô cực tốt (Dòng tiền vào, cập nhật mạng lưới, quỹ lớn mua).
    - -1 (Bán): Có tin xấu (Hack, rớt mạng, SEC kiện cáo).
    - 0 (Giữ): Tin tức trung lập, hoặc không có tin gì đáng chú ý.
    
    YÊU CẦU ĐẦU RA (TỐI QUAN TRỌNG):
    - CHỈ trả về một mảng JSON 4 số nguyên. Ví dụ: [1, 0, -1, 1].
    - Tuyệt đối KHÔNG GIẢI THÍCH, KHÔNG CHÀO HỎI, KHÔNG DÙNG MARKDOWN.
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # Bọc lót bằng Regex: Chặn mọi trường hợp Gemini tự nhiên "trình bày"
        match = re.search(r'\[\s*(-?[01])\s*,\s*(-?[01])\s*,\s*(-?[01])\s*,\s*(-?[01])\s*\]', raw_text)
        if match:
            return json.loads(match.group(0))
        else:
            return[0, 0, 0, 0] # Lỗi format thì trả về Hold cho an toàn
            
    except Exception as e:
        print(f"Lỗi khi gọi Google API: {e}")
        return[0, 0, 0, 0]

def get_final_trading_signals(news_context):
    """Hàm chạy song song 3 luồng AI và chốt số đông (Majority Vote)"""
    print("🤖 Đang đẩy dữ liệu cho Google Gemini phân tích (Chạy 3 luồng AI song song)...")
    results =[]
    
    # Chạy 3 request cùng lúc
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures =[executor.submit(get_single_ai_evaluation, news_context) for _ in range(3)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    print(f"-> Kết quả AI đọc 3 lần độc lập (Tránh ảo giác): {results}")
    
    # Tính "Số đông áp đảo" để chốt mảng cuối cùng
    final_signal =[]
    for i in range(len(COINS)):
        coin_signals = [res[i] for res in results]
        most_common = Counter(coin_signals).most_common(1)[0][0] # Lấy số xuất hiện nhiều nhất
        final_signal.append(most_common)
        
    return final_signal

# ==========================================
# 4. CHẠY THỰC TẾ (DEMO)
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 BẮT ĐẦU KHỞI ĐỘNG MODULE TÌM KIẾM VÀ PHÂN TÍCH 🚀")
    print("=" * 50)
    
    # Bước 1: Gọi Tavily lấy tin thật
    real_news = get_tavily_news(COINS)
    print(f"\n[Dữ liệu thô thu được từ Tavily]:\n{real_news}\n")
    
    # Bước 2: Đẩy tin vào AI và ép ra mảng số
    if real_news != "Không có dữ liệu tin tức mới.":
        final_array = get_final_trading_signals(real_news)
        
        print("\n" + "=" * 50)
        print("🎯 DỮ LIỆU CUỐI CÙNG SẠCH 100% ĐỂ FEED CHO DEV TRADE 🎯")
        print(f"Tài sản:   {COINS}")
        print(f"Tín hiệu:  {final_array}")
        print("=" * 50)
    else:
        print("❌ Demo thất bại do không cào được tin, hãy kiểm tra lại kết nối hoặc API Key!")