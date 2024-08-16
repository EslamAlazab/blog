from datetime import datetime, UTC
from bson import ObjectId
from typing import Annotated
from pymongo import ASCENDING
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from database import users, blogs
from models import User, BlogPost, Comment
from auth import create_access_token, user_dependency

app = FastAPI()

# User registration and login


@app.post("/register")
async def register(user: User):
    try:
        users.insert_one(user.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='username already used')


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.find_one({'username': form_data.username})
    if not user or user['password'] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)

    access_token = create_access_token(user['_id'], user['username'])
    return {"access_token": access_token, "token_type": "bearer"}

# CRUD operations for blog posts


@app.post("/posts/")
async def create_post(post: BlogPost, user: user_dependency):
    post_data = post.model_dump()

    # Add the author's user_id from the user dependency
    post_data['author'] = ObjectId(user['user_id'])

    # Handle the created_at field internally
    post_data['createdAt'] = datetime.now(UTC)

    # Insert the post into MongoDB
    result = blogs.insert_one(post_data)

    return {"postId": str(result.inserted_id)}


def serialize_blog_post(post: dict) -> dict:
    return {
        "_id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "author": str(post["author"]),
        "createdAt": post["createdAt"],
    }


@app.get("/posts/")
async def read_posts(page: Annotated[int, Query(ge=1)] = 1, size: Annotated[int, Query(ge=1)] = 10):
    start = (page - 1) * size
    result = blogs.find().skip(start).limit(size).sort('createdAt', ASCENDING)

    posts = [serialize_blog_post(post) for post in result]
    return posts


@app.put("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(post_id: str, post: BlogPost, user: user_dependency):
    post_data = post.model_dump()
    post_data['updatedAt'] = datetime.now(UTC)

    blogs.update_one({'_id': ObjectId(post_id), 'author': user['user_id']}, {
        '$set': post_data})


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, user: user_dependency):
    blogs.delete_one({'_id': ObjectId(post_id), 'author': user['user_id']})
    pass
