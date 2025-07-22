"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
similar_img_models.py
"""
import os


class SimilarImgModel:

    def __init__(self, file_dir: str, file_name: str, cosine_distance: float):
        self.file_dir: str = file_dir
        self.file_name: str = file_name
        self.cosine_distance: float = cosine_distance
        self.file_relative_path: str = str(os.path.join(self.file_dir, self.file_name))
