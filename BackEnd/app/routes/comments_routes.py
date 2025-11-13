from typing import List
from ..model import Comment,User,Post
from ..schemas import Comments,CommentsResponse
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from fastapi import APIRouter,Depends
from ..auth.jwt_handler import token_validation

router=APIRouter()

@router.post("/posts/{post_id}/addComment")
def addComments(post_id:int,comment:Comments, db:Session = Depends(get_db), current_user:dict = Depends(token_validation)):
    post_data=Comment(**comment.model_dump())
    post_data.post_id=post_id
    post_data.user_id=current_user["id"]
    db.add(post_data)
    db.commit()
    return {
        "status": "success",
        "message": "Comment posted successfully",
        "comment": post_data
    }
 
@router.put("/posts/{post_id}/updateComment/{comment_id}")    #Edit Comment
def update_comment(comment_id:int,updated_comment:Comments,db:Session=Depends(get_db),current_user:dict = Depends(token_validation)):
    comment=db.query(Comment).filter_by(id=comment_id).first()
    comment.content=updated_comment.content
    db.commit() 
    return {"status":"success"}

@router.delete("/deleteComment/{comment_id}")
def delete_Comment(comment_id:int,db:Session = Depends(get_db),current_user:dict = Depends(token_validation)):
    comment= db.query(Comment).filter_by(id=comment_id).first()
    db.delete(comment)
    db.commit()
    return "Comment Deleted"

@router.get("/posts/{post_id}/comments")   #Display All Comments on post
def comments(post_id:int,db:Session=Depends(get_db)):
    comments=db.query(Comment, User.username).join(User).filter(Comment.post_id == post_id).all()
    result=[]
    for comment,username in comments:
        result.append({ "id" : comment.id,"username" :username, "content": comment.content,"created_at":comment.created_at })        
    return result

@router.get("/user/{user_id}/comments")   # Display User Comments
def get_user_comments(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(token_validation)):
    comments_query = (db.query(Post, Comment)
                      .join(Comment, Comment.post_id == Post.id)
                      .join(User, User.id == Comment.user_id)
                      .filter(Comment.user_id == user_id)
                      .all())
    
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