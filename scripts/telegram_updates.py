import requests
import json
import io
import asyncio
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path
import re

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')
UPDATED_MODULES_ENV = os.getenv('UPDATED_MODULES')

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

def convert_markdown_to_html(markdown_text: str) -> str:
    """
    将Markdown格式转换为Telegram支持的HTML格式
    支持：粗体，斜体，代码块，链接，列表等
    """
    if not markdown_text or markdown_text == "暂无更新日志":
        return "<i>暂无更新日志</i>"
        
    # 处理代码块 (必须先处理，避免内部格式被处理)
    code_blocks = []
    def replace_code_block(match):
        code = match.group(1).strip()
        code_blocks.append(code)
        return f"CODE_BLOCK_{len(code_blocks)-1}_PLACEHOLDER"
    
    # 替换多行代码块
    markdown_text = re.sub(r'```(?:\w+)?\n(.*?)\n```', replace_code_block, markdown_text, flags=re.DOTALL)
    
    # 替换标题为加粗 (# 标题)
    markdown_text = re.sub(r'^#{1,6}\s+(.*?)$', r'<b>\1</b>', markdown_text, flags=re.MULTILINE)
    
    # 替换粗体 **文本** 或 __文本__
    markdown_text = re.sub(r'\*\*(.*?)\*\*|__(.*?)__', r'<b>\1\2</b>', markdown_text)
    
    # 替换斜体 *文本* 或 _文本_
    markdown_text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.*?)(?<!_)_(?!_)', r'<i>\1\2</i>', markdown_text)
    
    # 替换行内代码 `代码`
    markdown_text = re.sub(r'`(.*?)`', r'<code>\1</code>', markdown_text)
    
    # 替换链接 [文本](URL)
    markdown_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', markdown_text)
    
    # 替换有序列表项 1. 文本
    markdown_text = re.sub(r'^\d+\.\s+(.*?)$', r'• \1', markdown_text, flags=re.MULTILINE)
    
    # 替换无序列表项 - 文本 或 * 文本
    markdown_text = re.sub(r'^[\-\*]\s+(.*?)$', r'• \1', markdown_text, flags=re.MULTILINE)
    
    # 恢复代码块
    for i, code in enumerate(code_blocks):
        markdown_text = markdown_text.replace(f"CODE_BLOCK_{i}_PLACEHOLDER", f"<pre>{code}</pre>")
    
    # 替换段落分隔（保持适当的空行）
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
    
    # 为每个换行处添加一些格式，使在Telegram中显示更美观
    lines = markdown_text.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        # 如果是空行，直接添加
        if not line.strip():
            formatted_lines.append(line)
            continue
            
        # 如果是列表项，给它添加适当的缩进
        if line.strip().startswith('• '):
            formatted_lines.append(line)
        # 如果是标题（已转为加粗），添加前后空行
        elif line.strip().startswith('<b>') and line.strip().endswith('</b>'):
            if i > 0 and formatted_lines[-1].strip():
                formatted_lines.append('')
            formatted_lines.append(line)
            formatted_lines.append('')
        else:
            formatted_lines.append(line)
    
    result = '\n'.join(formatted_lines)
    
    # 添加格式化标记以确保在Telegram中换行正常
    result = result.replace('\n\n', '\n\n')
    
    return result

def check_for_module_updates() -> bool:
    """检查模块更新并发送通知，返回是否有更新"""
    try:
        validate_env()

        has_updates = False
        main_data = load_json_file('modules.json', {"modules": []})
        last_versions = load_json_file('last_versions.json', {})
        
        print("="*50)
        print("开始检查模块更新")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"REPO_ROOT: {REPO_ROOT}")
        print(f"环境变量 UPDATED_MODULES_ENV: {UPDATED_MODULES_ENV}")
        print("="*50)
        
        # 增强版日志查找逻辑
        updated_modules = set()
        
        # 0. 首先尝试从环境变量中获取更新的模块列表
        if UPDATED_MODULES_ENV:
            try:
                # 去除可能的单引号或双引号
                cleaned_json = UPDATED_MODULES_ENV.strip("'").strip('"')
                print(f"从环境变量中读取更新模块: {cleaned_json}")
                
                # 处理空数组的情况
                if cleaned_json == "[]" or not cleaned_json:
                    print("环境变量中没有更新模块")
                else:
                    try:
                        env_modules = json.loads(cleaned_json)
                        if env_modules and isinstance(env_modules, list):
                            for module_id in env_modules:
                                updated_modules.add(module_id)
                                print(f"从环境变量中发现模块更新: {module_id}")
                    except json.JSONDecodeError:
                        # 尝试解析非标准JSON格式
                        if '[' in cleaned_json and ']' in cleaned_json:
                            items = cleaned_json.strip('[]').split(',')
                            for item in items:
                                module_id = item.strip().strip('"').strip("'")
                                if module_id:
                                    updated_modules.add(module_id)
                                    print(f"从非标准JSON格式中发现模块更新: {module_id}")
            except Exception as e:
                print(f"解析环境变量UPDATED_MODULES时出错: {e}")
                print(f"环境变量内容: {UPDATED_MODULES_ENV}")
        
        # 如果环境变量中没有找到更新的模块，则继续使用其他方式检测
        if not updated_modules:
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
                                
                                # 使用更精确的正则表达式匹配更新记录
                                update_pattern = r"update: \[([^\]]+)\] -> update to"
                                matches = re.findall(update_pattern, content)
                                
                                for module_id in matches:
                                    updated_modules.add(module_id)
                                    print(f"从日志中发现模块更新: {module_id}")
                                    
                                # 如果没有使用正则表达式找到匹配，退回到行匹配
                                if not matches:
                                    for line in content.splitlines():
                                        if 'update: [' in line and '] -> update to' in line:
                                            try:
                                                module_id = line.split('[')[1].split(']')[0]
                                                updated_modules.add(module_id)
                                                print(f"从日志行中发现模块更新: {module_id}")
                                            except:
                                                print(f"无法从行中解析模块ID: {line}")
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
                        
                        # 处理不同的last_versions格式
                        if isinstance(last_record, dict):
                            last_version_code = last_record.get("versionCode", 0)
                        else:  # 旧格式，直接存储版本代码
                            last_version_code = last_record
                        
                        if isinstance(last_version_code, int) and isinstance(version_code, int):
                            if version_code > last_version_code:
                                updated_modules.add(id)
                                print(f"通过版本比较发现更新: {id} ({last_version_code} -> {version_code})")
            
        print(f"找到 {len(updated_modules)} 个更新的模块: {', '.join(updated_modules)}")

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
                    # 优先获取最新版本的更新日志文件
                    module_dir = REPO_ROOT / "modules" / id
                    print(f"正在查找模块 {id} 的更新日志文件...")
                    
                    # 优先尝试找最新版本的文件
                    latest_version_file = module_dir / f"{latest.get('version')}_{latest.get('versionCode')}.md"
                    if latest_version_file.exists():
                        print(f"找到最新版本更新日志文件: {latest_version_file}")
                        with open(latest_version_file, 'r', encoding='utf-8') as f:
                            changelog_content = f.read().strip()
                    else:
                        # 查找模块目录下的所有md文件
                        md_files = list(module_dir.glob("*.md"))
                        if md_files:
                            # 尝试根据版本号和构建号找到匹配的文件
                            version_files = [f for f in md_files if f.name.startswith(f"{version}_") or f.name.startswith(f"{version}{version_code}")]
                            if version_files:
                                changelog_file = version_files[0]
                                print(f"找到版本匹配的更新日志文件: {changelog_file}")
                                with open(changelog_file, 'r', encoding='utf-8') as f:
                                    changelog_content = f.read().strip()
                            else:
                                # 没有找到匹配的版本文件，查找最新修改的md文件
                                newest_file = max(md_files, key=lambda x: x.stat().st_mtime)
                                print(f"找到最新修改的MD文件: {newest_file}")
                                with open(newest_file, 'r', encoding='utf-8') as f:
                                    changelog_content = f.read().strip()
                        else:
                            # 尝试标准的changelog文件
                            for changelog_file in [module_dir / "changelog.md", module_dir / "CHANGELOG.md"]:
                                if changelog_file.exists():
                                    print(f"找到标准更新日志文件: {changelog_file}")
                                    with open(changelog_file, 'r', encoding='utf-8') as f:
                                        changelog_content = f.read().strip()
                                    break
                    
                    # 将Markdown转换为HTML格式
                    if changelog_content != "暂无更新日志":
                        changelog_content = convert_markdown_to_html(changelog_content)
                        # 如果内容过长，进行裁剪
                        if len(changelog_content) > 1500:
                            changelog_content = changelog_content[:1497] + "..."
                            
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
{changelog_content}

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
