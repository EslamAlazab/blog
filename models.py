from pydantic import BaseModel, Field
from datetime import datetime, UTC


class BlogPost(BaseModel):
    title: str
    content: str
    # created_at: datetime = Field(
    #     default_factory=lambda: datetime.now(UTC), alias='createdAt')
    # updated_at: datetime | None = Field(default=None, alias='updatedAt')


class Comment(BaseModel):
    post_id: str | None = Field(default=None, alias='_id')
    author: str
    content: str
    created_at: datetime = Field(
        default_factory=datetime.now, alias='createdAt')


class User(BaseModel):
    username: str
    password: str

    # user_id: str | None = Field(default=None, alias='_id')
