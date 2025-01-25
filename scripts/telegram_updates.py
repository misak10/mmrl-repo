import requests
import json
import requests
import io
import asyncio
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

main_data = {}
with open('json/modules.json') as f:
    main_data = json.load(f)

async def send_telegram_message(message, buttons):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'message_thread_id': 127,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': buttons
        })
    }
    
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

    response = requests.get(photo_url)
    response.raise_for_status()

    image_file = io.BytesIO(response.content)
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'message_thread_id': 127,
        'caption': caption,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': buttons
        })
    }
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
    except Exception as err:
        print(f"An error occurred: {err}")
        
    return "Done"

def check_for_module_updates():
    try:
        last_versions = {}
        
        # 更安全的文件读取和处理
        try:
            if os.path.exists('json/last_versions.json'):
                with open('json/last_versions.json', 'r') as f:
                    content = f.read().strip()
                    if content:  # 确保文件不为空
                        try:
                            last_versions = json.loads(content)
                        except json.JSONDecodeError:
                            print("JSON文件格式错误，重置为空字典")
                            last_versions = {}
            else:
                # 如果文件不存在，创建目录和空文件
                os.makedirs('json', exist_ok=True)
                with open('json/last_versions.json', 'w') as f:
                    json.dump({}, f, indent=2)
        except Exception as e:
            print(f"处理版本文件时出错: {e}")
            last_versions = {}

        for module in main_data.get("modules", []):
            id = module.get("id")
            name = module.get("name")
            version = module.get("version")
            version_code = module.get("versionCode")
            source = module.get("track").get("source")
            desc = module.get("description")
            author = module.get("author")
            donate = module.get("donate")
            support = module.get("support")
            latest = module.get("versions")[-1]
 
            if id not in last_versions or last_versions[id] != version_code:
                message = f"""🔰 <b>{name}</b>

📱 <b>版本信息</b>
└─ <code>{version}</code> (Build {version_code})

📝 <b>模块描述</b>
└─ {desc}

{f'''💬 <b>更新说明</b>
└─ <i>{module.get("note").get("message")}</i>

''' if module.get("note") and module.get("note").get("message") else ""}👨‍💻 <b>开发者</b>
└─ {author}

📢 <b>频道关注</b>
└─ @module_update

#模块更新 #{id}"""

                section_1 = []
                support_urls = []
                section_2 = []

                if latest.get("zipUrl"):
                    section_1.append({'text': '📦 下载安装包', 'url': latest.get("zipUrl")})

                if source:
                    support_urls.append({'text': '📂 源码仓库', 'url': source})
                if support:
                    support_urls.append({'text': '💭 交流反馈', 'url': support})
                if donate:
                    section_2.append({'text': '🎁 支持开发者', 'url': donate})

                buttons = [section_1,support_urls,section_2]

                if not module.get("cover"):
                    result = asyncio.run(send_telegram_message(message, buttons))
                else:
                    result = asyncio.run(send_telegram_photo(module.get("cover"), message, buttons))
                    
                last_versions[id] = version_code

                print(result)

        # 更安全的文件保存
        try:
            os.makedirs('json', exist_ok=True)
            with open('json/last_versions.json', 'w') as f:
                json.dump(last_versions, f, indent=2)
        except Exception as e:
            print(f"保存版本文件时出错: {e}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_for_module_updates()
