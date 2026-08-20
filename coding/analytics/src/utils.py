import yaml
from pathlib import Path
from typing import Any

def load_yaml_file(file_path: Path) -> Any:
    """
    Đọc file YAML từ đối tượng Path và trả về biến dữ liệu để truy xuất.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file YAML tại: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    return data
