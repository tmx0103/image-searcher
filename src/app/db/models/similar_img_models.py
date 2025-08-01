"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
similar_img_models.py
"""


class SimilarImgModel:

    def __init__(self, file_path: str, file_name: str, cosine_distance: float, file_sha256: str):
        self.filePath: str = file_path
        self.fileName: str = file_name
        self.cosineDistance: float = cosine_distance
        self.fileSha256: str = file_sha256
