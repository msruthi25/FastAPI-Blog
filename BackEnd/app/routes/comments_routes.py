from typing import List
from ..model import Comment,User,Post
from ..schemas import Comments,CommentsResponse
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from fastapi import APIRouter,Depends, HTTPException
from ..auth.jwt_handler import token_validation
from ..logger.logger import log
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

router=APIRouter()

@router.post("/posts/{post_id}/addComment")
async def addComments(post_id:int,comment:Comments, db:AsyncSession  = Depends(get_db), current_user:dict = Depends(token_validation)):
    try:
        post_data=Comment(**comment.model_dump())
        post_data.post_id=post_id
        post_data.user_id=current_user["id"]
        db.add(post_data)
        await db.commit()
        log.info("Comment created successfully", user_id=post_data.user_id, post_id=post_id)
        return {
            "status": "success",
            "message": "Comment posted successfully",
            "comment": post_data}
    except Exception as e:
        log.error("Error creating comment",post_id=post_id, error=str(e))
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}")
 

@router.put("/posts/{post_id}/updateComment/{comment_id}")
async def update_comment(
    comment_id: int,
    updated_comment: Comments,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(token_validation)
):
    try:
        stmt = select(Comment).filter_by(id=comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            log.warning("Comment not found for update", comment_id=comment_id)
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.user_id != current_user["id"]:
            log.error("Unauthorized user tried to edit comment", comment_id=comment_id, user_id=comment.user_id)
            raise HTTPException(status_code=403, detail="You cannot edit this comment")

        comment.content = updated_comment.content
        await db.commit()
        await db.refresh(comment)

        log.info("Comment updated successfully", comment_id=comment_id, user_id=comment.user_id)
        return {"status": "success", "updated_comment": comment.content}
    except HTTPException:
        raise

    except Exception as e:
        log.error("Error updating comment", comment_id=comment_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")




@router.delete("/deleteComment/{comment_id}")
async def delete_Comment(comment_id:int,db:AsyncSession  = Depends(get_db),current_user:dict = Depends(token_validation)):
    try:        
        stmt = select(Comment).filter_by(id=comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        if not comment:
            log.warning("Comment not found for deletion", comment_id=comment_id)
            raise HTTPException(status_code=404,detail=f"Comment not Found")
        if comment.user_id != current_user["id"]:
            log.error("UnAuthorized User! You cannot Delete this comment", comment_id=comment_id, user_id=comment.user_id)
            raise HTTPException(status_code=403,detail=f"UnAuthorized User! You cannot Delete this comment")
        await db.delete(comment)
        await db.commit()
        log.info("Comment deleted successfully", comment_id=comment_id, user_id=comment.user_id)
        return "Comment Deleted"
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error deleting comment", comment_id=comment_id, user_id=comment.user_id, error=str(e))
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}") 


@router.get("/posts/{post_id}/comments")   #Display All Comments on post
async def comments(post_id:int,db:AsyncSession =Depends(get_db)):
    try:        
        stmt = select(Comment, User.username).join(User).filter(Comment.post_id == post_id)
        results = await db.execute(stmt)
        comments = results.all()

        result=[]
        for comment,username in comments:
          result.append({ "id" : comment.id,"username" :username, "content": comment.content,"created_at":comment.created_at })        
        log.info("Fetched all comments", total_comments=len(result))
        return result
    except Exception as e:
        log.error("Error fetching comments", error=str(e))
        raise HTTPException(status_code=500,detail=f"internal server error {str(e)}")


@router.get("/user/{user_id}/comments")  # Display User Comments
async def get_user_comments(user_id: int,db: AsyncSession = Depends(get_db), current_user: dict = Depends(token_validation)):
    try:
        stmt = (
            select(Post, Comment)
            .join(Comment, Comment.post_id == Post.id)
            .join(User, User.id == Comment.user_id)
            .filter(Comment.user_id == user_id)
        )
        result = await db.execute(stmt)
        rows = result.all()        
        if not rows:
            log.warning("No comments found for user", user_id=user_id)            
            raise HTTPException(status_code=404, detail="Comments not found")
        data_list = {}
        for post, comment in rows:
            if post.id not in data_list:
                data_list[post.id] = {
                    "post_id": post.id,
                    "post_title": post.title,
                    "comments": []
                }
            data_list[post.id]["comments"].append({
                "comment_id": comment.id,
                "content": comment.content
            })
        log.info("Fetched comments by user", user_id=user_id, total_comments=len(data_list))
        return {"status": "success", "data": data_list}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error fetching comments by user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
