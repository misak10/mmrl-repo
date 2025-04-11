import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

# 全局变量
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')
MODULE_DATA_DIR = os.getenv('MODULE_DATA_DIR', 'temp_module_data')
MODULE_IDS = os.getenv('UPDATED_MODULE_IDS', '')

# 常量
REPO_URL = "https://misak10.github.io/mmrl-repo/"

def get_module_ids() -> List[str]:
    """获取需要通知的模块ID列表"""
    # 从环境变量获取
    if MODULE_IDS:
        module_ids = [mid.strip() for mid in MODULE_IDS.split() if mid.strip()]
        if module_ids:
            print(f"从环境变量获取到的模块ID: {', '.join(module_ids)}")
            return module_ids
    
    # 从目录结构获取
    if os.path.isdir(MODULE_DATA_DIR):
        module_ids = [
            d for d in os.listdir(MODULE_DATA_DIR) 
            if os.path.isdir(os.path.join(MODULE_DATA_DIR, d))
        ]
        if module_ids:
            print(f"从目录结构获取到的模块ID: {', '.join(module_ids)}")
            return module_ids
    
    print("警告: 未找到任何模块ID")
    return []

def get_module_info(module_id: str) -> Dict[str, Any]:
    """获取模块的详细信息"""
    info_file = os.path.join(MODULE_DATA_DIR, module_id, 'info.json')
    if os.path.isfile(info_file):
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                return info
        except json.JSONDecodeError:
            print(f"警告: 模块 {module_id} 的info.json格式无效")
        except Exception as e:
            print(f"读取模块信息时出错: {e}")
    
    # 返回默认信息
    return {
        "id": module_id,
        "name": module_id,
        "version": "未知",
        "versionCode": -1,
        "author": "未知"
    }

def get_changelog(module_id: str) -> str:
    """获取模块的更新日志"""
    changelog_file = os.path.join(MODULE_DATA_DIR, module_id, 'changelog.md')
    if os.path.isfile(changelog_file):
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取更新日志时出错: {e}")
    
    return "暂无更新日志"

def convert_markdown_to_html(markdown_text: str) -> str:
    """将Markdown转换为简单的HTML格式"""
    if not markdown_text or markdown_text == "暂无更新日志":
        return "<i>暂无更新日志</i>"
    
    # 简单替换，不做复杂处理
    html = markdown_text
    # 替换标题
    html = html.replace("# ", "<b>").replace("\n## ", "\n<b>")
    html = html.replace("\n# ", "\n<b>")
    
    # 在标题后添加</b>
    lines = []
    for line in html.split("\n"):
        if line.startswith("<b>"):
            line = f"{line}</b>"
        lines.append(line)
    
    html = "\n".join(lines)
    
    # 替换其他格式
    html = html.replace("**", "<b>").replace("**", "</b>")
    html = html.replace("*", "<i>").replace("*", "</i>")
    html = html.replace("`", "<code>").replace("`", "</code>")
    
    # 如果内容过长进行截断
    if len(html) > 1000:
        html = html[:997] + "..."
    
    return html

def send_telegram_notification(module_info: Dict[str, Any], changelog: str) -> bool:
    """发送Telegram通知"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("错误: 缺少Telegram配置，无法发送通知")
        return False

    module_id = module_info.get("id", "unknown")
    name = module_info.get("name", module_id)
    version = module_info.get("version", "未知")
    version_code = module_info.get("versionCode", -1)
    author = module_info.get("author", "未知")
    
    # 转换更新日志格式
    changelog_html = convert_markdown_to_html(changelog)
    
    # 构建消息内容
    message = f"""<b>🆕 模块更新</b>

<b>📦 模块信息</b>
├ 名称：<code>{name}</code>
├ 版本：<code>{version}</code>
└ 构建：<code>{version_code}</code>

<b>📝 更新日志</b>
{changelog_html}

<b>👨‍💻 开发者信息</b>
└ {author}

<b>🔗 相关链接</b>
└ <a href="{REPO_URL}">模块仓库</a>

<b>🏷️ 标签</b>
└ #模块更新 #{module_id}"""

    # 构建按钮
    buttons = [[{
        'text': '🌐 访问仓库',
        'url': REPO_URL
    }]]
    
    # 发送消息
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': buttons
        })
    }
    
    # 如果有话题ID，添加到payload
    if TELEGRAM_TOPIC_ID:
        try:
            topic_id = int(TELEGRAM_TOPIC_ID)
            if topic_id > 0:
                payload['message_thread_id'] = topic_id
        except ValueError:
            print("警告: TELEGRAM_TOPIC_ID 格式无效")
    
    try:
        print(f"正在发送模块 {module_id} 的更新通知...")
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"模块 {module_id} 的通知发送成功")
        return True
    except Exception as e:
        print(f"发送通知失败: {e}")
        return False

def main():
    """主函数"""
    try:
        print("开始执行模块更新通知...")
        
        # 获取需要通知的模块ID
        module_ids = get_module_ids()
        if not module_ids:
            print("没有找到需要通知的模块，结束执行")
            return
        
        success_count = 0
        total_count = len(module_ids)
        
        # 遍历处理每个模块
        for module_id in module_ids:
            print(f"处理模块: {module_id}")
            
            # 获取模块信息和更新日志
            module_info = get_module_info(module_id)
            changelog = get_changelog(module_id)
            
            # 发送通知
            if send_telegram_notification(module_info, changelog):
                success_count += 1
        
        print(f"通知处理完成，总计 {total_count} 个模块，成功发送 {success_count} 个通知")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 