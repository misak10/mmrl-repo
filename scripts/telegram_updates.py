import requests
import json
import io
import asyncio
import os
import sys
from typing import Dict, List, Optional

# 从环境变量获取配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')

# 验证必要的环境变量
def validate_env():
    missing_vars = []
    if not TELEGRAM_BOT_TOKEN:
        missing_vars.append('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_CHAT_ID:
        missing_vars.append('TELEGRAM_CHAT_ID')
    
    if missing_vars:
        print(f"错误: 缺少必要的环境变量: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # 确保CHAT_ID是数字格式
    try:
        int(TELEGRAM_CHAT_ID)
    except ValueError:
        print("错误: TELEGRAM_CHAT_ID 必须是数字格式")
        sys.exit(1)

def load_json_file(file_path: str, default: Dict = None) -> Dict:
    """安全地加载 JSON 文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
    return default if default is not None else {}

def save_json_file(file_path: str, data: Dict) -> None:
    """安全地保存 JSON 文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存文件 {file_path} 时出错: {e}")

async def send_telegram_message(message, buttons):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': buttons
        })
    }

    # 如果设置了话题ID，添加到payload中
    if TELEGRAM_TOPIC_ID:
        try:
            topic_id = int(TELEGRAM_TOPIC_ID)
            if topic_id > 0:
                payload['message_thread_id'] = topic_id
        except ValueError:
            print("警告: TELEGRAM_TOPIC_ID 格式无效，将发送到主群组")
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Message sent: {message}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response: {response.json()}")
    except Exception as err:
        print(f"An error occurred: {err}")
        
    return "Done"

async def send_telegram_photo(photo_url, caption, buttons):
    """Send a photo from a URL with a caption to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        response = requests.get(photo_url)
        response.raise_for_status()
    except Exception as e:
        print(f"获取图片失败: {e}")
        # 如果获取图片失败，改用发送消息
        return await send_telegram_message(caption, buttons)

    image_file = io.BytesIO(response.content)
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': caption,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': buttons
        })
    }

    # 如果设置了话题ID，添加到payload中
    if TELEGRAM_TOPIC_ID:
        try:
            topic_id = int(TELEGRAM_TOPIC_ID)
            if topic_id > 0:
                payload['message_thread_id'] = topic_id
        except ValueError:
            print("警告: TELEGRAM_TOPIC_ID 格式无效，将发送到主群组")

    files = {
        'photo': ('image.jpg', image_file, 'image/jpeg')
    }

    try:
        response = requests.post(url, data=payload, files=files)
        response.raise_for_status()
        print(f"Photo sent successfully with caption: {caption}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response: {response.text}")
        # 如果发送图片失败，尝试发送纯文本消息
        return await send_telegram_message(caption, buttons)
    except Exception as err:
        print(f"An error occurred: {err}")
        return await send_telegram_message(caption, buttons)
        
    return "Done"

def check_for_module_updates() -> bool:
    """检查模块更新并发送通知，返回是否有更新"""
    try:
        # 验证环境变量
        validate_env()

        has_updates = False
        main_data = load_json_file('json/modules.json', {"modules": []})
        last_versions = load_json_file('json/last_versions.json', {})

        for module in main_data.get("modules", []):
            id = module.get("id")
            version_code = module.get("versionCode")
            
            if id not in last_versions or last_versions[id] != version_code:
                has_updates = True
                name = module.get("name")
                version = module.get("version")
                desc = module.get("description")
                author = module.get("author")
                donate = module.get("donate")
                support = module.get("support")
                source = module.get("track", {}).get("source")
                latest = module.get("versions", [{}])[-1]

                # 构建更新说明部分
                update_note = ""
                if module.get("note") and module.get("note").get("message"):
                    note_message = module.get("note").get("message")
                    # 如果更新说明太长，进行截断
                    if len(note_message) > 300:
                        note_message = note_message[:297] + "..."
                    update_note = f'''💬 <b>更新说明</b>
└─ <i>{note_message}</i>

'''

                message = f"""<b>🔰 模块更新通知</b>

📦 <b>{name}</b>
├ <code>{version}</code> (Build {version_code})
└ <i>{desc}</i>

{update_note}👨‍💻 <b>开发者信息</b>
└ {author}

🌐 <b>相关链接</b>
└ <a href="https://misak10.github.io/mmrl-repo/">模块仓库</a>

#模块更新 #{id}"""

                section_1 = []
                support_urls = []
                section_2 = []

                # 下载按钮
                if latest.get("zipUrl"):
                    section_1.append({
                        'text': '📥 下载安装包',
                        'url': latest.get("zipUrl")
                    })

                # 相关链接按钮
                if source:
                    support_urls.append({
                        'text': '📂 源码仓库',
                        'url': source
                    })
                if support:
                    support_urls.append({
                        'text': '💭 交流反馈',
                        'url': support
                    })

                # 打赏按钮
                if donate:
                    section_2.append({
                        'text': '🎁 支持开发者',
                        'url': donate
                    })

                # 添加仓库按钮
                section_2.append({
                    'text': '📱 访问仓库',
                    'url': 'https://misak10.github.io/mmrl-repo/'
                })

                buttons = [section_1, support_urls, section_2]

                try:
                    if not module.get("cover"):
                        result = asyncio.run(send_telegram_message(message, buttons))
                    else:
                        result = asyncio.run(send_telegram_photo(module.get("cover"), message, buttons))
                        
                    last_versions[id] = version_code
                    print(result)
                except Exception as e:
                    print(f"发送通知失败 (模块 {id}): {e}")
                    continue

        save_json_file('json/last_versions.json', last_versions)
        return has_updates

    except Exception as e:
        print(f"检查更新时发生错误: {e}")
        return False

if __name__ == "__main__":
    has_updates = check_for_module_updates()
    print(f"模块更新检查完成，{'有' if has_updates else '没有'}更新")
