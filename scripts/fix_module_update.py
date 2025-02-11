#!/usr/bin/env python3

import os
import json
import sys
import requests
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import time

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
        self.base_url = "https://misak10.github.io/mmrl-repo"
        
    def generate_urls(self, module_id: str, version: str, version_code: int) -> tuple[str, str]:
        """生成 zip 和 changelog 的 URL"""
        file_base_name = f"{version}_{version_code}"
        base_path = f"{self.base_url}/modules/{module_id}/{file_base_name}"
        return f"{base_path}.zip", f"{base_path}.md"

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

    def update_local_update_json(self, remote_update: Dict[str, Any]) -> bool:
        """更新本地的 update.json 文件"""
        try:
            if self.update_file.exists():
                with open(self.update_file, 'r', encoding='utf-8') as f:
                    local_update = json.load(f)
            else:
                local_update = {
                    "versions": [],
                    "timestamp": time.time()
                }

            # 获取模块 ID
            module_id = self.module_path.name

            # 合并远程版本信息
            if "versions" not in local_update:
                local_update["versions"] = []
                
            # 获取现有版本列表
            existing_versions = {v["version"] for v in local_update["versions"]}
            
            # 添加新版本
            if isinstance(remote_update.get("versions"), list):
                for version in remote_update["versions"]:
                    if version["version"] not in existing_versions:
                        # 生成正确的 URL
                        zip_url, changelog_url = self.generate_urls(
                            module_id,
                            version["version"],
                            version["versionCode"]
                        )
                        
                        # 获取 zip 文件大小
                        try:
                            response = requests.head(version["zipUrl"], timeout=30)
                            size = int(response.headers.get('content-length', 0))
                        except:
                            size = 0
                            
                        version_info = {
                            "timestamp": time.time(),
                            "version": version["version"],
                            "versionCode": version["versionCode"],
                            "zipUrl": zip_url,
                            "changelog": changelog_url,
                            "size": size
                        }
                        local_update["versions"].append(version_info)
            else:
                # 处理单个版本的情况
                if remote_update["version"] not in existing_versions:
                    # 生成正确的 URL
                    zip_url, changelog_url = self.generate_urls(
                        module_id,
                        remote_update["version"],
                        remote_update.get("versionCode", 0)
                    )
                    
                    # 获取 zip 文件大小
                    try:
                        response = requests.head(remote_update["zipUrl"], timeout=30)
                        size = int(response.headers.get('content-length', 0))
                    except:
                        size = 0
                        
                    version_info = {
                        "timestamp": time.time(),
                        "version": remote_update["version"],
                        "versionCode": remote_update.get("versionCode", 0),
                        "zipUrl": zip_url,
                        "changelog": changelog_url,
                        "size": size
                    }
                    local_update["versions"].append(version_info)

            # 更新主时间戳
            local_update["timestamp"] = time.time()

            # 保存更新后的 update.json
            with open(self.update_file, 'w', encoding='utf-8') as f:
                json.dump(local_update, f, indent=4)

            logger.info(f"Successfully updated {self.update_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to update local update.json: {e}")
            return False

    def download_module_zip(self, zip_url: str, version: str, version_code: int) -> bool:
        """下载模块的 zip 文件和 changelog"""
        try:
            # 构建文件名（格式：version_versionCode）
            file_base_name = f"{version}_{version_code}"
            
            # 确保模块目录存在
            self.module_path.mkdir(exist_ok=True)
            
            # 下载并保存 zip 文件
            response = requests.get(zip_url, timeout=30)
            response.raise_for_status()
            zip_path = self.module_path / f"{file_base_name}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # 尝试下载 changelog
            try:
                # 使用生成的 changelog URL
                changelog_url = zip_url.replace('.zip', '.md')
                changelog_response = requests.get(changelog_url, timeout=30)
                changelog_response.raise_for_status()
                changelog_path = self.module_path / f"{file_base_name}.md"
                with open(changelog_path, 'wb') as f:
                    f.write(changelog_response.content)
            except Exception as e:
                logger.warning(f"Failed to download changelog: {e}")
            
            logger.info(f"Successfully downloaded module files to {self.module_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download module files: {e}")
            return False

    def get_latest_version_code(self, update_data: Dict[str, Any]) -> Optional[int]:
        """获取更新信息中的最新版本号"""
        try:
            if isinstance(update_data.get("versions"), list) and update_data["versions"]:
                return update_data["versions"][0]["versionCode"]
            elif "versionCode" in update_data:
                return update_data["versionCode"]
            return None
        except Exception:
            return None

    def get_local_latest_version_code(self) -> Optional[int]:
        """获取本地最新版本号"""
        try:
            if not self.update_file.exists():
                return None
                
            with open(self.update_file, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
                
            if isinstance(local_data.get("versions"), list) and local_data["versions"]:
                return local_data["versions"][0]["versionCode"]
            return None
        except Exception:
            return None

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

        # 检查版本
        remote_version = self.get_latest_version_code(remote_update)
        local_version = self.get_local_latest_version_code()
        
        if remote_version is None:
            logger.error("Failed to get remote version code")
            return False
            
        if local_version is not None and remote_version <= local_version:
            logger.info(f"Local version ({local_version}) is already up to date")
            return True

        # 更新本地 update.json
        if not self.update_local_update_json(remote_update):
            return False

        # 下载最新版本的文件
        if isinstance(remote_update.get("versions"), list) and remote_update["versions"]:
            latest_version = remote_update["versions"][0]
            return self.download_module_zip(
                latest_version["zipUrl"],
                latest_version["version"],
                latest_version["versionCode"]
            )
        elif "version" in remote_update and "versionCode" in remote_update:
            return self.download_module_zip(
                remote_update["zipUrl"],
                remote_update["version"],
                remote_update["versionCode"]
            )
        else:
            logger.error("No valid version information found in update.json")
            return False

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
