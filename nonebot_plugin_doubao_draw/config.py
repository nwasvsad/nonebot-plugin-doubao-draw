from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    doubao_draw_api_key: str = ""
    doubao_draw_enabled: bool = True
    doubao_draw_size: str = "2K"
    doubao_draw_groups: List[int] = []
    doubao_draw_superadmins: List[int] = []
