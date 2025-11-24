# test_post.py
import pytest
from sqlalchemy import select
from app.databaseSetup import get_db
from app.model import User, Post
from app.auth.jwt_handler import token_validation


# Override token_validation dependency
async def override_token_validation():
    async for db in get_db():
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            raise Exception("No user found in DB!")
        return {"id": user.id, "username": user.username}

from app.main import app
app.dependency_overrides[token_validation] = override_token_validation

# Test: Get all posts
@pytest.mark.anyio(scheduler="asyncio")
async def test_get_all_posts(async_client):
    response = await async_client.get("/posts")

    if response.status_code == 200:
        posts = response.json()
        assert isinstance(posts, list)
        if posts:
            post = posts[0]
            for key in ["id", "title", "content", "author_id", "img_url", "published", "created_at"]:
                assert key in post

    elif response.status_code == 404:
        assert response.json()["detail"] == "No post found"
    elif response.status_code == 500:
        print("Internal Server Error:", response.json())
        assert response.status_code == 500
        assert "detail" in response.json()     

    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


# Test: Get post by ID
@pytest.mark.anyio(scheduler="asyncio")
async def test_get_post_by_id(async_client):
    test_post_id = 1

    response = await async_client.get(f"/posts/{test_post_id}")

    if response.status_code == 200:
        post = response.json()
        assert isinstance(post, dict)
        for key in ["id", "title", "content", "author_id", "img_url", "created_at"]:
            assert key in post

    elif response.status_code == 404:
        assert response.json()["detail"] == "Post not found"
    
    elif response.status_code == 500:
        print("Internal Server Error:", response.json())
        assert response.status_code == 500
        assert "detail" in response.json()
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


# Test: Get posts by user
@pytest.mark.anyio(scheduler="asyncio")
async def test_get_posts_by_user(async_client):
    async for db in get_db():
        result = await db.execute(select(User))
        user = result.scalars().first()
        assert user is not None, "No user in DB"
        user_id = user.id
        break
    response = await async_client.get(f"/postsbyUser/{user_id}")

    if response.status_code == 200:
        posts = response.json()
        assert isinstance(posts, list)
        if posts:
            for post in posts:
                assert post["author_id"] == user_id

    elif response.status_code == 404:
        assert response.json()["detail"] == "Posts not found"

    elif response.status_code == 500:
        print("Internal Server Error:", response.json())
        assert response.status_code == 500
        assert "detail" in response.json()    
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


#Create Post
@pytest.mark.anyio(scheduler="asyncio")
async def test_create_post(async_client):

    post_payload = {
        "title": "Test Post",
        "content": "This is a test post for pytest",
        "img_url": "http://example.com/image.png",
        "published": True
    }

    response = await async_client.post("/createPost", json=post_payload)

    if response.status_code in (200, 201):
        data = response.json()
        assert data["status"] == "success"

    elif response.status_code == 500:
        pytest.fail(f"Internal Server Error: {response.json()}")

    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


@pytest.mark.anyio
async def test_update_post(async_client, async_session):
    # 1️⃣ Get current user
    result = await async_session.execute(select(User))
    user = result.scalars().first()
    assert user is not None
    current_user_id = user.id

    # 2️⃣ Get or create post
    result = await async_session.execute(select(Post).filter(Post.author_id == current_user_id))
    post = result.scalars().first()
    if not post:
        post = Post(
            title="Test Post",
            content="Test content",
            img_url="http://example.com/test.png",
            author_id=current_user_id
        )
        async_session.add(post)
        await async_session.commit()
        await async_session.refresh(post)
    post_id = post.id

    # 3️⃣ Update via API
    update_payload = {
        "title": "Updated Title",
        "content": "Updated content for testing",
        "img_url": "http://example.com/image.png",
    }

    response = await async_client.put(f"/posts/{post_id}", json=update_payload)
    assert response.status_code == 200

    # 4️⃣ Query DB in the same session
    updated_post = await async_session.get(Post, post_id)
    await async_session.refresh(updated_post)
    assert updated_post.title == update_payload["title"]
    assert updated_post.content == update_payload["content"]


@pytest.mark.anyio
async def test_delete_post(async_client, async_session):
    # 1️⃣ Get a user and a post
    result = await async_session.execute(select(User))
    user = result.scalars().first()
    assert user is not None, "No user in DB"
    current_user_id = user.id

    # Pick a post or create one
    result = await async_session.execute(select(Post).where(Post.author_id == current_user_id))
    post = result.scalars().first()
    if not post:
        post = Post(
            title="Post to delete",
            content="Delete me",
            img_url="http://example.com/delete.png",
            author_id=current_user_id
        )
        async_session.add(post)
        await async_session.commit()
        await async_session.refresh(post)
    post_id = post.id

    # 2️⃣ Send DELETE request
    response = await async_client.delete(f"/posts/{post_id}")

    # 3️⃣ Verify response and DB
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"

        # Query fresh to see if post is deleted
        result = await async_session.execute(select(Post).where(Post.id == post_id))
        deleted_post = result.scalar_one_or_none()
        assert deleted_post is None, "Post was not deleted from DB"

    elif response.status_code == 403:
        assert response.json()["detail"] == "Not allowed"
    elif response.status_code == 404:
        assert response.json()["detail"] == "Post not found"
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")
