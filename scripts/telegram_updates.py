import requests
import json
import io
import asyncio
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = SCRIPT_DIR.parent

def get_json_path(filename: str) -> Path:
    """获取JSON文件的完整路径"""
    json_dir = REPO_ROOT / 'json'
    return json_dir / filename

def validate_env():
    missing_vars = []
    if not TELEGRAM_BOT_TOKEN:
        missing_vars.append('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_CHAT_ID:
        missing_vars.append('TELEGRAM_CHAT_ID')
    
    if missing_vars:
        print(f"错误: 缺少必要的环境变量: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        int(TELEGRAM_CHAT_ID)
    except ValueError:
        print("错误: TELEGRAM_CHAT_ID 必须是数字格式")
        sys.exit(1)

def load_json_file(file_path: str, default: Dict = None) -> Dict:
    """安全地加载 JSON 文件"""
    try:
        full_path = get_json_path(os.path.basename(file_path))
        print(f"正在加载文件: {full_path}")
        
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误 ({full_path}): {e}")
                        print(f"文件内容: {content[:100]}...")
                else:
                    print(f"警告: 文件为空 ({full_path})")
        else:
            print(f"警告: 文件不存在 ({full_path})")
            if default is not None:
                save_json_file(file_path, default)
                return default
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
    return default if default is not None else {}

def save_json_file(file_path: str, data: Dict) -> None:
    """安全地保存 JSON 文件"""
    try:
        full_path = get_json_path(os.path.basename(file_path))
        print(f"正在保存文件: {full_path}")
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"文件保存成功: {full_path}")
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

    if TELEGRAM_TOPIC_ID:
        try:
            topic_id = int(TELEGRAM_TOPIC_ID)
            if topic_id > 0:
                payload['message_thread_id'] = topic_id
                print(f"将消息发送到话题 ID: {topic_id}")
        except ValueError:
            print("警告: TELEGRAM_TOPIC_ID 格式无效，将发送到主群组")
    
    try:
        print(f"正在发送消息到 Telegram: chat_id={TELEGRAM_CHAT_ID}")
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"消息发送成功: {message[:100]}...")
        print(f"Telegram API 响应: {response.status_code}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"响应: {response.json()}")
    except Exception as err:
        print(f"发生错误: {err}")
        
    return "Done"

async def send_telegram_photo(photo_url, caption, buttons):
    """Send a photo from a URL with a caption to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        response = requests.get(photo_url)
        response.raise_for_status()
    except Exception as e:
        print(f"获取图片失败: {e}")
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
        return await send_telegram_message(caption, buttons)
    except Exception as err:
        print(f"An error occurred: {err}")
        return await send_telegram_message(caption, buttons)
        
    return "Done"

def check_for_module_updates() -> bool:
    """检查模块更新并发送通知，返回是否有更新"""
    try:
        validate_env()

        has_updates = False
        main_data = load_json_file('modules.json', {"modules": []})
        last_versions = load_json_file('last_versions.json', {})
        
        # 增强版日志查找逻辑
        updated_modules = set()
        
        # 1. 尝试从多个可能的位置查找日志文件
        possible_log_dirs = [
            REPO_ROOT / 'log',
            REPO_ROOT,
            Path('log'),
            Path('.'),
            Path('/github/workspace/log')
        ]
        
        print("开始查找日志文件...")
        for log_dir in possible_log_dirs:
            if not log_dir.exists():
                print(f"目录不存在: {log_dir}")
                continue
                
            print(f"在目录中查找日志: {log_dir}")
            try:
                all_files = list(log_dir.glob('*'))
                print(f"该目录中的所有文件: {[str(f) for f in all_files]}")
                
                log_files = list(log_dir.glob('*sync*.log'))
                print(f"找到的日志文件: {[str(f) for f in log_files]}")
                
                for log_file in log_files:
                    print(f"正在读取日志文件: {log_file}")
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(f"日志文件内容片段: {content[:200]}...")
                            
                            for line in content.splitlines():
                                if 'update: [' in line and '] -> update to' in line:
                                    module_id = line.split('[')[1].split(']')[0]
                                    updated_modules.add(module_id)
                                    print(f"从日志中发现模块更新: {module_id}")
                    except Exception as e:
                        print(f"读取日志文件 {log_file} 时出错: {e}")
            except Exception as e:
                print(f"处理目录 {log_dir} 时出错: {e}")
        
        # 2. 如果没有找到更新，尝试从modules.json和last_versions.json比较版本
        if not updated_modules:
            print("从日志中未找到更新，尝试比较版本文件...")
            for module in main_data.get("modules", []):
                id = module.get("id")
                version_code = module.get("versionCode", 0)
                
                if id in last_versions:
                    last_record = last_versions.get(id, {})
                    last_version_code = last_record.get("versionCode", 0)
                    
                    if isinstance(last_version_code, int) and isinstance(version_code, int):
                        if version_code > last_version_code:
                            updated_modules.add(id)
                            print(f"通过版本比较发现更新: {id} ({last_version_code} -> {version_code})")
        
        # 3. 直接检查lingeringsound_ads模块(临时措施)
        if "lingeringsound_ads" not in updated_modules:
            for module in main_data.get("modules", []):
                if module.get("id") == "lingeringsound_ads":
                    current_version = module.get("version", "")
                    current_code = module.get("versionCode", 0)
                    last_record = last_versions.get("lingeringsound_ads", {})
                    
                    if isinstance(last_record, dict):
                        last_version = last_record.get("version", "")
                        last_code = last_record.get("versionCode", 0)
                    else:
                        last_version = ""
                        last_code = 0
                    
                    print(f"lingeringsound_ads 当前版本: {current_version} ({current_code})")
                    print(f"lingeringsound_ads 上次记录版本: {last_version} ({last_code})")
                    
                    if current_version != last_version or current_code != last_code:
                        updated_modules.add("lingeringsound_ads")
                        print(f"检测到 lingeringsound_ads 有更新: {last_version} -> {current_version}")
        
        print(f"从日志中找到 {len(updated_modules)} 个更新的模块: {', '.join(updated_modules)}")

        for module in main_data.get("modules", []):
            id = module.get("id")
            
            if id in updated_modules:
                has_updates = True
                version_code = module.get("versionCode")
                name = module.get("name")
                version = module.get("version")
                desc = module.get("description")
                author = module.get("author")
                donate = module.get("donate")
                support = module.get("support")
                source = module.get("track", {}).get("source")
                latest = module.get("versions", [{}])[-1]

                changelog_content = "暂无更新日志"
                try:
                    changelog_file = REPO_ROOT / "modules" / id / f"{latest['version']}_{latest['versionCode']}.md"
                    if changelog_file.exists():
                        with open(changelog_file, 'r', encoding='utf-8') as f:
                            changelog_content = f.read().strip()
                            if len(changelog_content) > 300:
                                changelog_content = changelog_content[:297] + "..."
                except Exception as e:
                    print(f"读取更新日志失败 ({id}): {e}")

                update_note = ""
                if module.get("note") and module.get("note").get("message"):
                    note_message = module.get("note").get("message")
                    if len(note_message) > 300:
                        note_message = note_message[:297] + "..."
                    update_note = f'''📢 <b>更新说明</b>
└ <i>{note_message}</i>

'''

                message = f"""<b>🎉 模块更新通知</b>

<b>📦 模块信息</b>
├ 名称：<code>{name}</code>
├ 版本：<code>{version}</code>
└ 构建：<code>{version_code}</code>

{update_note}<b>📝 更新日志</b>
└ <i>{changelog_content}</i>

<b>👨‍💻 开发者信息</b>
└ {author}

<b>🔗 相关链接</b>
└ <a href="https://misak10.github.io/mmrl-repo/">模块仓库</a>

<b>🏷️ 标签</b>
└ #模块更新 #{id}"""

                section_1 = []
                support_urls = []
                section_2 = []

                if latest.get("zipUrl"):
                    section_1.append({
                        'text': '📥 下载安装包',
                        'url': latest.get("zipUrl")
                    })

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

                if donate:
                    section_2.append({
                        'text': '🎁 支持开发者',
                        'url': donate
                    })

                section_2.append({
                    'text': '🌐 访问仓库',
                    'url': 'https://misak10.github.io/mmrl-repo/'
                })

                buttons = [section_1, support_urls, section_2]

                try:
                    print(f"开始发送模块 {id} 的更新通知...")
                    if not module.get("cover"):
                        result = asyncio.run(send_telegram_message(message, buttons))
                    else:
                        result = asyncio.run(send_telegram_photo(module.get("cover"), message, buttons))
                        
                    # 保存已通知的版本
                    if isinstance(last_versions.get(id), dict):
                        last_versions[id]["version"] = version
                        last_versions[id]["versionCode"] = version_code
                    else:
                        last_versions[id] = {
                            "version": version,
                            "versionCode": version_code,
                            "author": author,
                            "name": name
                        }
                    print(f"通知结果: {result}")
                except Exception as e:
                    print(f"发送通知失败 (模块 {id}): {e}")
                    continue

        save_json_file('last_versions.json', last_versions)
        return has_updates

    except Exception as e:
        print(f"检查更新时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    has_updates = check_for_module_updates()
    print(f"模块更新检查完成，{'有' if has_updates else '没有'}更新")
