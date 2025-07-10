"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
"""
import hashlib


def sha256_file(file_path) -> str:
    hash_obj = hashlib.new('sha256')
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def sha256_string(input_str: str) -> str:
    sha256_hash = hashlib.sha256()  # 创建哈希对象
    sha256_hash.update(input_str.encode('utf-8'))  # 编码为字节并更新哈希[2,5](@ref)
    return sha256_hash.hexdigest()