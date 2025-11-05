from ..model import Comment
from ..schemas import Comments
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from fastapi import APIRouter,Depends


router=APIRouter()

@router.post("posts/{id}/addComment")
def addComments(comment:Comments, db:Session = Depends(get_db)):
    post_data=Comment(**comment.model_dump())
    db.add(post_data)
    db.commit()
    return "Comment added"

@router.get("posts/{id}/comments")
def comments(id:int):
    return "Comments"
