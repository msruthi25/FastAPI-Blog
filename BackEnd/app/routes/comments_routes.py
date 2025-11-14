from typing import List
from ..model import Comment,User,Post
from ..schemas import Comments,CommentsResponse
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from fastapi import APIRouter,Depends, HTTPException
from ..auth.jwt_handler import token_validation

router=APIRouter()

@router.post("/posts/{post_id}/addComment")
def addComments(post_id:int,comment:Comments, db:Session = Depends(get_db), current_user:dict = Depends(token_validation)):
    try:
        post_data=Comment(**comment.model_dump())
        post_data.post_id=post_id
        post_data.user_id=current_user["id"]
        db.add(post_data)
        db.commit()
        return {
            "status": "success",
            "message": "Comment posted successfully",
            "comment": post_data}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}")
 
@router.put("/posts/{post_id}/updateComment/{comment_id}")    #Edit Comment
def update_comment(comment_id:int,updated_comment:Comments,db:Session=Depends(get_db),current_user:dict = Depends(token_validation)):
    try:
        comment=db.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            raise HTTPException(status_code=404,detail=f"Comment not Found")
        if comment.user_id!=current_user["id"]:
            raise HTTPException(status_code=403,detail=f"You cannot edit this Comment")
        comment.content=updated_comment.content
        db.commit() 
        return {"status":"success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")

@router.delete("/deleteComment/{comment_id}")
def delete_Comment(comment_id:int,db:Session = Depends(get_db),current_user:dict = Depends(token_validation)):
    try:        
        comment= db.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            raise HTTPException(status_code=404,detail=f"Comment not Found")
        if comment.user_id != current_user["id"]:
            raise HTTPException(status_code=403,detail=f"UnAuthorized User! You cannot Delete this comment")
        db.delete(comment)
        db.commit()
        return "Comment Deleted"
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}") 

@router.get("/posts/{post_id}/comments")   #Display All Comments on post
def comments(post_id:int,db:Session=Depends(get_db)):
    try:
        comments=db.query(Comment, User.username).join(User).filter(Comment.post_id == post_id).all()
        result=[]
        for comment,username in comments:
          result.append({ "id" : comment.id,"username" :username, "content": comment.content,"created_at":comment.created_at })        
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"internal server error {str(e)}")

@router.get("/user/{user_id}/comments")   # Display User Comments
def get_user_comments(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(token_validation)):
    try:
        comments_query = (db.query(Post, Comment)
                        .join(Comment, Comment.post_id == Post.id)
                        .join(User, User.id == Comment.user_id)
                        .filter(Comment.user_id == user_id)
                        .all())
        if  not comments_query:
            raise HTTPException(status_code=404,detail="Post not Found")    
        data_list = {}   
        for post, comment in comments_query:
            exists = any(value["post_id"] == post.id for value in data_list.values())        
            if not exists:
                data_list[post.id] = {
                    "post_id": post.id,
                    "post_title": post.title,
                    "comments": []
                }       
            if data_list[post.id]["post_id"] == comment.post_id:
                data_list[post.id]["comments"].append({
                    "comment_id": comment.id,
                    "content": comment.content
            })
        return {"status": "success", "data": data_list}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}")