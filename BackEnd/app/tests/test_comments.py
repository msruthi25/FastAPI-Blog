# test_comments.py
import pytest
from sqlalchemy import select
from app.databaseSetup import get_db
from app.model import User, Post, Comment
from app.auth.jwt_handler import token_validation
from app.main import app


async def override_token_validation():
    async for db in get_db():
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            raise Exception("No user found in DB!")
        return {"id": user.id, "username": user.username}

app.dependency_overrides[token_validation] = override_token_validation


async def get_test_user():
    async for db in get_db():
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            raise Exception("No user found in DB!")
        return user


async def get_or_create_post(current_user_id, session):
    result = await session.execute(select(Post).where(Post.author_id == current_user_id))
    post = result.scalars().first()
    if not post:
        post = Post(title="Test Post", content="Test content", author_id=current_user_id)
        session.add(post)
        await session.commit()
        await session.refresh(post)
    return post


async def get_or_create_comment(current_user_id, post_id, session, content="Test comment"):
    result = await session.execute(
        select(Comment).where(Comment.user_id == current_user_id, Comment.post_id == post_id)
    )
    comment = result.scalars().first()
    if not comment:
        comment = Comment(content=content, post_id=post_id, user_id=current_user_id)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
    return comment

@pytest.mark.anyio
async def test_add_comment(async_client, async_session):
    user = await get_test_user()
    post = await get_or_create_post(user.id, async_session)

    # Ensure FastAPI sees the same session
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    payload = {"content": "This is a test comment"}
    response = await async_client.post(f"/posts/{post.id}/addComment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "comment" in data

@pytest.mark.anyio
async def test_update_comment(async_client, async_session):
    user = await get_test_user()
    post = await get_or_create_post(user.id, async_session)
    comment = await get_or_create_comment(user.id, post.id, async_session, content="Old comment")

    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    payload = {"content": "Updated comment content"}
    response = await async_client.put(f"/posts/{post.id}/updateComment/{comment.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["updated_comment"] == payload["content"]

@pytest.mark.anyio
async def test_delete_comment(async_client, async_session):
    user = await get_test_user()
    post = await get_or_create_post(user.id, async_session)
    comment = await get_or_create_comment(user.id, post.id, async_session, content="Comment to delete")

    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    response = await async_client.delete(f"/deleteComment/{comment.id}")
    assert response.status_code == 200
    assert response.json() == "Comment Deleted"


@pytest.mark.anyio
async def test_get_post_comments(async_client, async_session):
    user = await get_test_user()
    post = await get_or_create_post(user.id, async_session)

    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    response = await async_client.get(f"/posts/{post.id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)


@pytest.mark.anyio
async def test_get_user_comments(async_client, async_session):
    user = await get_test_user()

    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    response = await async_client.get(f"/user/{user.id}/comments")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
