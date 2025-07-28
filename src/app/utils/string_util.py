"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
string_util.py
"""


class StringUtil:
    def __init__(self):
        pass

    @classmethod
    def concat(cls, *args):
        result = ""
        for arg in args:
            if type(arg) == str:
                result += arg
        return result
