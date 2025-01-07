import requests
import json
import io
import asyncio
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram 配置缺失")
            
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_message(self, message: str, buttons: List[List[Dict[str, str]]]) -> str:
        """发送文本消息到Telegram"""
        url = f"{self.api_base}/sendMessage"
        payload = self._prepare_payload(message, buttons)
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            logger.info(f"消息发送成功: {message[:100]}...")
            return "成功"
        except Exception as e:
            logger.error(f"发送消息时出错: {str(e)}")
            return f"失败: {str(e)}"

    async def send_photo(self, photo_url: str, caption: str, buttons: List[List[Dict[str, str]]]) -> str:
        """发送图片消息到Telegram"""
        url = f"{self.api_base}/sendPhoto"
        
        try:
            # 获取图片
            photo_response = requests.get(photo_url)
            photo_response.raise_for_status()
            image_file = io.BytesIO(photo_response.content)
            
            payload = self._prepare_payload(caption, buttons)
            files = {'photo': ('image.jpg', image_file, 'image/jpeg')}
            
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
            logger.info(f"图片消息发送成功: {caption[:100]}...")
            return "成功"
        except Exception as e:
            logger.error(f"发送图片消息时出错: {str(e)}")
            return f"失败: {str(e)}"

    def _prepare_payload(self, text: str, buttons: List[List[Dict[str, str]]]) -> Dict[str, str]:
        """准备请求负载"""
        return {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': buttons})
        }

class ModuleUpdateChecker:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.main_data = self._load_json('json/modules.json')
        self.last_versions = self._load_json('json/last_versions.json', default={})

    def _load_json(self, filepath: str, default: Any = None) -> Dict:
        """加载JSON文件"""
        try:
            with open(filepath) as f:
                return json.load(f)
        except FileNotFoundError:
            return default if default is not None else {}

    def _save_last_versions(self):
        """保存最新版本信息"""
        with open('json/last_versions.json', 'w') as f:
            json.dump(self.last_versions, f, indent=2)

    def _format_message(self, module: Dict[str, Any]) -> str:
        """格式化模块更新消息"""
        note = module.get("note", {}).get("message", "")
        desc = module["description"]
        
        message = f"""<b>{module['name']}</b>
<i>版本:</i> {module['version']} ({module['versionCode']})

📃 {desc}
{f'<blockquote>{note}</blockquote>' if note else ''}

<b>作者:</b> {module['author']}
<b>关注:</b> @module_update"""
        
        return message

    def _prepare_buttons(self, module: Dict[str, Any]) -> List[List[Dict[str, str]]]:
        """准备按钮配置"""
        latest = module['versions'][-1]
        buttons = []
        
        # 下载按钮
        if latest.get("zipUrl"):
            buttons.append([{'text': '📦 下载', 'url': latest['zipUrl']}])
            
        # 支持链接
        support_buttons = []
        if module['track'].get('source'):
            support_buttons.append({'text': '源码', 'url': module['track']['source']})
        if module.get('support'):
            support_buttons.append({'text': '支持', 'url': module['support']})
        if support_buttons:
            buttons.append(support_buttons)
            
        # 捐赠按钮
        if module.get('donate'):
            buttons.append([{'text': '捐赠', 'url': module['donate']}])
            
        return buttons

    async def check_updates(self):
        """检查模块更新"""
        try:
            for module in self.main_data.get("modules", []):
                module_id = module['id']
                version_code = module['versionCode']
                
                if module_id not in self.last_versions or self.last_versions[module_id] != version_code:
                    message = self._format_message(module)
                    buttons = self._prepare_buttons(module)
                    
                    if module.get("cover"):
                        result = await self.notifier.send_photo(module["cover"], message, buttons)
                    else:
                        result = await self.notifier.send_message(message, buttons)
                        
                    logger.info(f"模块 {module_id} 更新通知: {result}")
                    self.last_versions[module_id] = version_code
            
            self._save_last_versions()
            
        except Exception as e:
            logger.error(f"检查更新时出错: {str(e)}")
            raise

def main():
    """主函数"""
    try:
        checker = ModuleUpdateChecker()
        asyncio.run(checker.check_updates())
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
