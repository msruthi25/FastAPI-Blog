from fastapi import APIRouter, Depends
from ..model import Post
from ..schemas import PostResponse,PostModel
from ..databaseSetup import get_db
from sqlalchemy.orm import Session
from typing import List
from ..auth.jwt_handler import token_validation

router=APIRouter()

@router.get("/posts",response_model= List[PostResponse])  
def getAllposts(db:Session=Depends(get_db)):  #Get All posts
    allpost_list = db.query(Post).all()
    print(allpost_list)
    return allpost_list 


@router.get("/posts/{id}",response_model=PostResponse)
def getPostById(id:int,db:Session=Depends(get_db)):   #Get post by ID
    post=db.query(Post).filter_by(id=id).first()  
    return post

@router.post("/createPost")
def create_post(post:PostModel,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #Create Post
    post_data=Post(**post.model_dump())
    post_data.author_id=current_user["id"] 
    db.add(post_data)
    db.commit()
    return "Post created"


@router.put("/update/{id}")
def update_post(id:int,post:dict,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #update Post
    db.query(Post).filter(Post.id==id).update(post)  
    db.commit() 
    return "updated"

@router.delete("/delete/{id}")
def delete_data(id:int, db:Session = Depends(get_db),current_user = Depends(token_validation)):  #Delete Post
    db.query(Post).filter_by(id=id).delete()
    db.commit()
    return "data deleted"

