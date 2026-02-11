from typing import TypedDict

class State(TypedDict):
  raw_data:str
  prompt:str
  title : str
  content : str
  topic: str
  img_url:str
  is_valid: bool
  validation_errors : list
  attempt_count: int 