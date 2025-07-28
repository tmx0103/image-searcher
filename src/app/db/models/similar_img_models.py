"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
similar_img_models.py
"""
import os


class SimilarImgModel:

    def __init__(self, file_dir: str, file_name: str, cosine_distance: float, file_sha256: str):
        self.fileDir: str = file_dir
        self.fileName: str = file_name
        self.cosineDistance: float = cosine_distance
        self.fileRelativePath: str = str(os.path.join(self.fileDir, self.fileName))
        self.fileSha256: str = file_sha256
