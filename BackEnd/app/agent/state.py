from typing import Optional, TypedDict, List

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
  tool_calls: list
  research_papers: list
  image_context: Optional[str] 
  news_items: Optional[List[dict]]
  news_source: Optional[str] 