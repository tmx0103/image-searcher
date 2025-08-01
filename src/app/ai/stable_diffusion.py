"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
stable_diffusion.py
"""
import base64
import io
import os
import uuid
from threading import Lock

import requests
from PIL import Image

from src.app.log.logger import logger


class StableDiffusion:
    _instance = None
    _lock = Lock()
    _url = os.getenv("SD_WEB_UI_URL")

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = StableDiffusion()
        return cls._instance

    def __init__(self):
        pass

    def prepare_mask(self, image_path):
        """生成白色蒙版区域（mask_area格式: [x, y, width, height]）"""
        img = Image.open(image_path).convert("RGB")
        mask = Image.new("RGB", img.size, (255, 255, 255))

        return img, mask

    def image_to_base64(self, pil_image):
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def write_file(self, data, file_dir, file_name):
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(os.path.join(file_dir, file_name), "wb") as f:
            f.write(data)

    def generate_image(self, prompt, image_path):
        logger.info(f"提示词:{prompt},图片路径:{image_path}")
        orig_img, mask_img = self.prepare_mask(image_path)
        orig_base64 = self.image_to_base64(orig_img)
        mask_base64 = self.image_to_base64(mask_img)
        payload = {
            "cfg_scale": 7,
            "init_images": [orig_base64],
            "mask": mask_base64,  # 关键：全白蒙版
            "prompt": prompt,  # 整图重绘的目标风格
            "denoising_strength": 0.75,  # 重绘幅度
            "inpaint_full_res": False,  # 禁用局部优化
            "inpaint_full_res_padding": 0,  # 无边缘扩展
            "mask_blur": 0,  # 无蒙版模糊
            "inpainting_fill": 1,  # 原图填充模式
            "steps": 20,
            "sampler_name": "DPM++ 2M"
        }
        response = requests.post(self._url, json=payload)
        result = response.json()
        output_data = base64.b64decode(result["images"][0].split(",", 1)[0])
        file_dir = "temp"
        file_name = f"output_{str(uuid.uuid4()).replace("-", "")}.png"
        logger.info(f"保存文件:{os.path.abspath(os.path.join(file_dir, file_name))}")
        self.write_file(output_data, file_dir, file_name)
        return os.path.join(file_dir, file_name)


if __name__ == "__main__":
    sd = StableDiffusion()
    print(sd.generate_image("white hair,blue eyes,1girl", "temp.png"))
