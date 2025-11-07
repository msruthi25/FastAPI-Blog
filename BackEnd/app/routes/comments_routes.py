from ..model import Comment
from ..schemas import Comments
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
    return "Comment added"
 
@router.put("/posts/{post_id}/updateComment/{comment_id}")    #Edit Comment
def update_comment(comment_id:int,updated_comment:Comments,db:Session=Depends(get_db)):
    comment=db.query(Comment).filter_by(id=comment_id).first()
    comment.content=updated_comment.content
    db.commit() 
    return "Update Comments"

@router.delete("/deleteComment/{comment_id}")
def delete_Comment(comment_id:int,db:Session = Depends(get_db),current_user:dict = Depends(token_validation)):
    comment= db.query(Comment).filter_by(id=comment_id).first()
    db.delete(comment)
    db.commit()
    return "Comment Deleted"

@router.get("/posts/{post_id}/comments")   #Display All Comments on post
def comments(post_id:int,db:Session=Depends(get_db)):
    comments=db.query(Comment).filter_by(post_id=post_id).all()
    return "Comments"