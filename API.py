import requests
import os
import re

# Thông tin cần thiết
ACCESS_TOKEN = "EAAP4LaQQKlMBOZBZBeJa3uhXRcZCqze1OYFKqa0KnZApeZCdJe6pextNbt0bzF6ziBaDMfPr3VC3dG93qafHzEHKB5d1JJZBH3ZAGi0LZBomQAATwhS4ndkLfsn6ezXAZAWlDlEbsHORHZAU5EKX4X00B73PsWX7qEjX3VcqxZAPJbTSZCKGY5lZCPNY925t630kTxS5ISu2EkKqyU0Wr3jVYx4dJ53JQwiJQFB7hhql0siJ1ZBrUDAzO40e9Ff4smQ3HS3ZC8ZD"  # Thay bằng Access Token của bạn
USER_ID = "100050299607423"                 # Thay bằng Page ID của trang
GRAPH_API_URL = f"https://graph.facebook.com/v16.0/{USER_ID}/posts?fields=message,attachments&access_token={ACCESS_TOKEN}"

# Tạo thư mục lưu hình ảnh và văn bản theo cấu trúc folder_user_id/images và folder_user_id/text
BASE_IMAGE_FOLDER = "downloaded"
USER_IMAGE_FOLDER = os.path.join(BASE_IMAGE_FOLDER, f"{USER_ID}/images")
USER_TEXT_FOLDER = os.path.join(BASE_IMAGE_FOLDER, f"{USER_ID}/text")
os.makedirs(USER_IMAGE_FOLDER, exist_ok=True)
os.makedirs(USER_TEXT_FOLDER, exist_ok=True)

def fetch_latest_post(api_url):
    """Lấy bài viết mới nhất từ Facebook Graph API"""
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]  # Bài viết mới nhất
    print("Không tìm thấy bài viết hoặc lỗi API.")
    return None

def download_image(image_url, save_path):
    """Tải hình ảnh từ URL về máy"""
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Đã tải ảnh về: {save_path}")
    else:
        print("Không tải được ảnh.")

def preprocess_text(text):
    """Tiền xử lý nội dung văn bản"""
    # Loại bỏ ký tự đặc biệt, chỉ giữ lại chữ và số
    text = re.sub(r"[^a-zA-Z0-9\s\u00C0-\u017F]", "", text)  # Bao gồm cả các ký tự UTF-8 như dấu tiếng Việt
    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    # Lấy bài viết mới nhất
    latest_post = fetch_latest_post(GRAPH_API_URL)
    if not latest_post:
        return

    # Trích xuất dữ liệu
    message = latest_post.get("message", "Nội dung không có.")
    attachments = latest_post.get("attachments", {}).get("data", [])
    image_urls = [attachment.get("media", {}).get("image", {}).get("src") for attachment in attachments]

    # Loại bỏ các ảnh không hợp lệ
    image_urls = [url for url in image_urls if url is not None]

    # Tiền xử lý nội dung văn bản
    processed_message = preprocess_text(message)
    print("Nội dung bài viết sau khi xử lý:")
    print(processed_message)

    # Lưu văn bản vào folder text
    text_file_name = f"{USER_ID}_post.txt"
    text_save_path = os.path.join(USER_TEXT_FOLDER, text_file_name)
    with open(text_save_path, "w", encoding='utf-8') as text_file:
        text_file.write(processed_message)
    print(f"Đã lưu văn bản bài viết vào: {text_save_path}")

    # Lưu tất cả ảnh nếu có
    for image_url in image_urls:
        image_name = os.path.basename(image_url.split("?")[0])  # Lấy tên file từ URL
        image_save_path = os.path.join(USER_IMAGE_FOLDER, image_name)
        download_image(image_url, image_save_path)

if __name__ == "__main__":
    main()
