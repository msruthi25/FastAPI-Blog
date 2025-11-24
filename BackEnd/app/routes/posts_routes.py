from fastapi import APIRouter, Depends, HTTPException
from ..model import Post,User
from ..schemas import PostResponse,PostModel, PostUpdateModel
from ..databaseSetup import get_db
from sqlalchemy.orm import Session
from typing import List
from ..auth.jwt_handler import token_validation
from ..logger.logger import log
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

router=APIRouter()

# Get All Posts
@router.get("/posts", response_model=List[PostResponse])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Post))
        allpost_list = result.scalars().all()
        if not allpost_list:
            log.warning("No posts found")
            raise HTTPException(status_code=404, detail="No post found")
        log.info("Fetched posts successfully", total_posts=len(allpost_list))
        return allpost_list
    except Exception as e:
        log.error("Error occurred during fetching posts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


#Get Post by UserID
@router.get("/postsbyUser/{user_id}", response_model=List[PostResponse])
async def get_posts_by_user(user_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(token_validation)):
    try:
        result = await db.execute(select(Post).filter_by(author_id=user_id))
        posts = result.scalars().all()
        if not posts:
            log.warning("No posts found for user", user_id=user_id)
            raise HTTPException(status_code=404, detail="Posts not found")
        log.info("Fetched posts for user", user_id=user_id, total_posts=len(posts))
        return posts
    except HTTPException:  
        raise
    except Exception as e:
        log.error("Unexpected error fetching posts by user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")



# Get Post by ID
@router.get("/posts/{id}")
async def get_post_by_id(id: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Post, User.username).join(User, User.id == Post.author_id).filter(Post.id == id)
        result = await db.execute(stmt)
        post_data = result.first()
        if not post_data:
            log.warning("No post found for Post ID", post_id=id)
            raise HTTPException(status_code=404, detail="Post not found")
        post, username = post_data
        log.info("Fetched post by Post ID", post_id=id)
        return {
            "id": post.id,
            "title": post.title,
            "author_id": post.author_id,
            "img_url": post.img_url,
            "username": username,
            "content": post.content,
            "created_at": post.created_at
        }
    except Exception as e:
        log.error("Error fetching post by Post ID", post_id=id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


# Create Post
@router.post("/createPost")
async def create_post(post: PostModel, db: AsyncSession = Depends(get_db), current_user=Depends(token_validation)):
    try:
        post_data = Post(**post.model_dump())
        post_data.author_id = current_user["id"]
        db.add(post_data)
        await db.commit()
        await db.refresh(post_data)
        log.info("Post created successfully", post_id=post_data.id, author_id=post_data.author_id)
        return {"status": "success"}
    except Exception as e:
        log.error("Error creating post", author_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


# Update Post
@router.put("/posts/{id}")
async def update_post(id: int, post: PostUpdateModel, db: AsyncSession = Depends(get_db), current_user=Depends(token_validation)):
    try:
        post_data = post.model_dump(exclude_unset=True)
        # Ensure the author matches
        stmt = select(Post).filter(Post.id == id)
        result = await db.execute(stmt)
        existing_post = result.scalar_one_or_none()
        if not existing_post:
            log.warning("Post not found for update", post_id=id)
            raise HTTPException(status_code=404, detail="Post not found")
        if existing_post.author_id != current_user["id"]:
            log.error("Not allowed to edit this post", post_id=id, author_id=current_user["id"])
            raise HTTPException(status_code=403, detail="Not allowed to edit this post")

        for key, value in post_data.items():
            setattr(existing_post, key, value)
        await db.commit()
        log.info("Post updated successfully", post_id=id, author_id=current_user["id"])
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error updating post", post_id=id, author_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


# Delete Post
@router.delete("/posts/{id}")
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user=Depends(token_validation)):
    try:
        stmt = select(Post).where(Post.id == id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if not post:
            log.warning("Post not found for deletion", post_id=id)
            raise HTTPException(status_code=404, detail="Post not found")
        if post.author_id != current_user["id"]:
            log.error("Unauthorized attempt to delete post", post_id=id, author_id=current_user["id"])
            raise HTTPException(status_code=403, detail="Not allowed")
        await db.delete(post)
        await db.commit()
        log.info("Post deleted successfully", post_id=id, author_id=current_user["id"])
        return {"status": "success", "message": "Post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error deleting post", post_id=id, author_id=current_user["id"], error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")
