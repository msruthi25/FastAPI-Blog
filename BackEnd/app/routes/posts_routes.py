from fastapi import APIRouter, Depends
from ..model import Post,User
from ..schemas import PostResponse,PostModel, PostUpdateModel
from ..databaseSetup import get_db
from sqlalchemy.orm import Session
from typing import List
from ..auth.jwt_handler import token_validation

router=APIRouter()

@router.get("/posts",response_model= List[PostResponse])  
def getAllposts(db:Session=Depends(get_db)):  #Get All posts
    allpost_list = db.query(Post).all()
    return allpost_list 


@router.get("/postsbyUser/{user_id}")
def getPostById(user_id:int,db:Session=Depends(get_db),response_model= List[PostResponse]):   #Get post by Author ID
    posts=db.query(Post).filter_by(author_id=user_id).all()    
    return posts

@router.get("/posts/{id}")
def getPostById(id:int,db:Session=Depends(get_db)):   #Get post by ID
    posts=db.query(Post, User.username).join(User, User.id == Post.author_id).filter(Post.id == id).first()
    post,username =posts
    return { "id" : post.id, "title":post.title,"author_id":post.author_id,"img_url":post.img_url, "username" :username, "content": post.content,"created_at":post.created_at }

@router.post("/createPost")
def create_post(post:PostModel,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #Create Post
    post_data=Post(**post.model_dump())
    post_data.author_id=current_user["id"] 
    db.add(post_data)
    db.commit()
    return {"status":"success"}


@router.put("/posts/{id}")
def update_post(id:int,post:PostUpdateModel,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #update Post
    post_data=post.model_dump(exclude_unset=True)
    db.query(Post).filter(Post.id==id).update(post_data)  
    db.commit() 
    return {"status":"success"}

@router.delete("/posts/{id}")
def delete_data(id: int, db: Session = Depends(get_db), current_user = Depends(token_validation)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        return {"status": "Post not found"}
    if post.author_id != current_user["id"]:
        return {"status": "You are not authorized to delete this post"}
    db.delete(post) 
    db.commit()
    return {"status": "success", "message": "Post deleted successfully"}

