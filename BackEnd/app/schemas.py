from typing import Optional
from pydantic import BaseModel,EmailStr, Field, HttpUrl, field_validator
from datetime import datetime
import bleach

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: int = Field(gt=0)
    title: str
    content: str
    author_id: int = Field(gt=0)
    img_url: str
    published: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("title", "content", mode="before")
    def sanitize_text(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)


class PostModel(BaseModel):
    title: str
    content: str
    img_url: str
    published: Optional[bool] = None 

    model_config = {"from_attributes": True}

    @field_validator("title", "content", mode="before")
    def sanitize_text(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)


class Comments(BaseModel):
    content: str

    model_config = {"from_attributes": True}

    @field_validator("content", mode="before")
    def sanitize_content(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)


class CommentsResponse(BaseModel):
    id: int = Field(gt=0)
    content: str
    username: str = Field(min_length=3, max_length=50)
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("content", mode="before")
    def sanitize_content(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)


class PostUpdateModel(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    img_url: Optional[str] = None
    author_id: Optional[int] = None  # optional now

    model_config = {"from_attributes": True}

    @field_validator("title", "content", mode="before")
    def sanitize_text(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)


class AIResponse(BaseModel):
    title: str
    content :str
    img_url :str

    model_config = {"from_attributes": True}

    @field_validator("content", mode="before")
    def sanitize_content(cls, v):
        allowed_tags = {"p", "b", "i", "u", "strong", "em", "a"}
        allowed_attrs = {"a": ["href", "title"]}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs)
