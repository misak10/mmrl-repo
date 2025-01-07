import requests
import json
import io
import asyncio
import os
import logging
import glob
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
        self.modules_data = self._load_modules_data()
        self.last_versions = self._load_json('json/last_versions.json', default={})
        self._sync_versions_file()

    def _load_json(self, filepath: str, default: Any = None) -> Dict:
        """加载JSON文件"""
        if default is None:
            default = {}

        # 如果文件不存在，直接返回默认值
        if not os.path.exists(filepath):
            logger.warning(f"文件不存在: {filepath}")
            return default

        try:
            # 直接尝试读取和解析JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, UnicodeDecodeError, IOError) as e:
            logger.error(f"读取JSON文件失败 {filepath}: {str(e)}")
            # 如果文件有问题，删除它并返回默认值
            try:
                os.remove(filepath)
                logger.info(f"已删除损坏的文件: {filepath}")
            except OSError:
                pass
            return default

    def _save_json(self, filepath: str, data: Dict):
        """保存JSON数据到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 直接保存JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"成功保存数据到: {filepath}")
        except Exception as e:
            logger.error(f"保存JSON文件失败 {filepath}: {str(e)}")

    def _load_modules_data(self) -> Dict[str, Dict]:
        """从modules文件夹加载所有模块数据"""
        modules_data = {}
        module_paths = glob.glob('modules/*/track.json')
        
        for path in module_paths:
            try:
                with open(path) as f:
                    module_data = json.load(f)
                    module_id = os.path.basename(os.path.dirname(path))
                    modules_data[module_id] = module_data
                    logger.debug(f"已加载模块 {module_id} 的数据")
            except Exception as e:
                logger.error(f"加载模块数据失败 {path}: {str(e)}")
                
        return modules_data

    def _sync_versions_file(self):
        """同步 last_versions.json 文件内容"""
        # 获取当前所有模块的版本信息
        current_modules = {}
        for module_id, module_data in self.modules_data.items():
            try:
                version_code = module_data.get("versionCode")
                if version_code is not None:
                    current_modules[module_id] = version_code
            except Exception as e:
                logger.error(f"处理模块 {module_id} 时出错: {str(e)}")
        
        # 使用新的字典替换旧的
        self.last_versions = current_modules
        
        # 保存更新后的版本信息
        self._save_json('json/last_versions.json', self.last_versions)
        logger.info("已更新 last_versions.json 文件")

    async def check_updates(self):
        """检查模块更新"""
        try:
            update_count = 0
            for module_id, module_data in self.modules_data.items():
                try:
                    version_code = module_data.get("versionCode")
                    if not version_code:
                        logger.warning(f"模块 {module_id} 缺少版本号信息")
                        continue

                    # 检查版本更新
                    if module_id not in self.last_versions:
                        logger.info(f"发现新模块: {module_id}")
                        update_needed = True
                    else:
                        current_version = self.last_versions[module_id]
                        update_needed = current_version != version_code
                        if update_needed:
                            logger.info(f"模块 {module_id} 有更新: {current_version} -> {version_code}")
                    
                    if update_needed:
                        message = self._format_message(module_data, module_id)
                        buttons = self._prepare_buttons(module_data)
                        
                        if module_data.get("cover"):
                            result = await self.notifier.send_photo(
                                module_data["cover"], message, buttons)
                        else:
                            result = await self.notifier.send_message(message, buttons)
                            
                        logger.info(f"模块 {module_id} 更新通知: {result}")
                        self.last_versions[module_id] = version_code
                        update_count += 1
                
                except Exception as e:
                    logger.error(f"处理模块 {module_id} 更新时出错: {str(e)}")
                    continue
            
            if update_count > 0:
                self._save_last_versions()
                logger.info(f"完成更新检查，发送了 {update_count} 个更新通知")
            else:
                logger.info("完成更新检查，没有发现新的更新")
            
        except Exception as e:
            logger.error(f"检查更新时出错: {str(e)}")
            raise

    def _format_message(self, module_data: Dict[str, Any], module_id: str) -> str:
        """格式化模块更新消息"""
        note = module_data.get("note", {}).get("message", "")
        desc = module_data.get("description", "")
        
        message = f"""<b>{module_data.get('name', module_id)}</b>
<i>版本:</i> {module_data.get('version')} ({module_data.get('versionCode')})

📃 {desc}
{f'<blockquote>{note}</blockquote>' if note else ''}

<b>作者:</b> {module_data.get('author', '未知')}
<b>关注:</b> @module_update"""
        
        return message

    def _prepare_buttons(self, module_data: Dict[str, Any]) -> List[List[Dict[str, str]]]:
        """准备按钮配置"""
        buttons = []
        versions = module_data.get('versions', [])
        
        if versions and versions[-1].get("zipUrl"):
            buttons.append([{'text': '📦 下载', 'url': versions[-1]["zipUrl"]}])
            
        support_buttons = []
        if module_data.get('track', {}).get('source'):
            support_buttons.append({'text': '源码', 'url': module_data['track']['source']})
        if module_data.get('support'):
            support_buttons.append({'text': '支持', 'url': module_data['support']})
        if support_buttons:
            buttons.append(support_buttons)
            
        if module_data.get('donate'):
            buttons.append([{'text': '捐赠', 'url': module_data['donate']}])
            
        return buttons

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
