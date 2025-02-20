from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 從環境變數中讀取 LINE CHANNEL ACCESS TOKEN
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

@app.route('/webhook', methods=['POST'])
def webhook():
    # 接收來自 IFTTT 的 JSON 資料
    body = request.get_json()
    group_id = body.get("groupId")  # 來自 IFTTT 的群組 ID
    text_message = body.get("message")   # 來自 IFTTT 的文字訊息內容
    image_url = body.get("imageUrl")  # 來自 IFTTT 的圖片 URL
    
    if group_id and (text_message or image_url):
        messages = []
        
        # 加入文字訊息（如果存在）
        if text_message:
            messages.append({"type": "text", "text": text_message})
        
        # 加入圖片訊息（如果存在）
        if image_url:
            messages.append({
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            })
        
        # 發送訊息到指定群組
        push_message_to_group(group_id, messages)
        return jsonify({'status': 'success'}), 200
    else:
        # 如果資料不完整，回應錯誤
        return jsonify({'status': 'error', 'message': 'Missing groupId, message, or imageUrl'}), 400

def push_message_to_group(group_id, messages):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': group_id,
        'messages': messages  # 支援多訊息陣列
    }
    # 發送 HTTP POST 請求到 LINE Messaging API 的 Push Message 端點
    response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        # 輸出錯誤訊息，方便除錯
        print(f"Failed to send message: {response.status_code} {response.text}")

if __name__ == '__main__':
    # 啟動 Flask Web 服務
    app.run(port=5000)
