#!/usr/bin/env python3

import os
import json
import sys
import requests
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModuleUpdater:
    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.track_file = self.module_path / 'track.json'
        self.update_file = self.module_path / 'update.json'
        
    def read_track_json(self) -> Optional[Dict[str, Any]]:
        """读取 track.json 文件"""
        try:
            if not self.track_file.exists():
                logger.error(f"track.json not found in {self.module_path}")
                return None
                
            with open(self.track_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse track.json in {self.module_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading track.json: {e}")
            return None

    def fetch_update_json(self, update_url: str) -> Optional[Dict[str, Any]]:
        """从 update_to URL 获取更新信息"""
        try:
            response = requests.get(update_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch update.json from {update_url}: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Failed to parse update.json from {update_url}")
            return None

    def download_module_zip(self, zip_url: str, version: str) -> bool:
        """下载模块的 zip 文件"""
        try:
            response = requests.get(zip_url, timeout=30)
            response.raise_for_status()
            
            # 确保版本目录存在
            version_dir = self.module_path / version
            version_dir.mkdir(exist_ok=True)
            
            # 保存 zip 文件
            zip_path = version_dir / f"{version}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded {zip_url} to {zip_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download module zip from {zip_url}: {e}")
            return False

    def update_local_update_json(self, remote_update: Dict[str, Any]) -> bool:
        """更新本地的 update.json 文件"""
        try:
            if self.update_file.exists():
                with open(self.update_file, 'r', encoding='utf-8') as f:
                    local_update = json.load(f)
            else:
                local_update = {"versions": []}

            # 合并远程版本信息
            if "versions" not in local_update:
                local_update["versions"] = []
                
            # 获取现有版本列表
            existing_versions = {v["version"] for v in local_update["versions"]}
            
            # 添加新版本
            if isinstance(remote_update.get("versions"), list):
                for version in remote_update["versions"]:
                    if version["version"] not in existing_versions:
                        local_update["versions"].append(version)
            else:
                # 处理单个版本的情况
                version_info = {
                    "version": remote_update["version"],
                    "versionCode": remote_update.get("versionCode", 0),
                    "zipUrl": remote_update["zipUrl"],
                    "changelog": remote_update.get("changelog", "")
                }
                if version_info["version"] not in existing_versions:
                    local_update["versions"].append(version_info)

            # 保存更新后的 update.json
            with open(self.update_file, 'w', encoding='utf-8') as f:
                json.dump(local_update, f, indent=4)

            logger.info(f"Successfully updated {self.update_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to update local update.json: {e}")
            return False

    def fix_module(self) -> bool:
        """修复模块更新"""
        # 读取 track.json
        track_data = self.read_track_json()
        if not track_data or "update_to" not in track_data:
            return False

        # 获取远程更新信息
        remote_update = self.fetch_update_json(track_data["update_to"])
        if not remote_update:
            return False

        # 更新本地 update.json
        if not self.update_local_update_json(remote_update):
            return False

        # 下载最新版本的 zip 文件
        if isinstance(remote_update.get("versions"), list):
            latest_version = remote_update["versions"][0]
        else:
            latest_version = remote_update

        return self.download_module_zip(
            latest_version["zipUrl"],
            latest_version["version"]
        )

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_module_update.py <module_path>")
        sys.exit(1)

    module_path = sys.argv[1]
    updater = ModuleUpdater(module_path)
    
    if updater.fix_module():
        logger.info(f"Successfully fixed module in {module_path}")
        sys.exit(0)
    else:
        logger.error(f"Failed to fix module in {module_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 