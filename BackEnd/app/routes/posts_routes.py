from fastapi import APIRouter, Depends, HTTPException
from ..model import Post,User
from ..schemas import PostResponse,PostModel, PostUpdateModel
from ..databaseSetup import get_db
from sqlalchemy.orm import Session
from typing import List
from ..auth.jwt_handler import token_validation

router=APIRouter()

@router.get("/posts",response_model= List[PostResponse])  
def getAllposts(db:Session=Depends(get_db)):  #Get All posts
    try:
       allpost_list = db.query(Post).all()
       if not allpost_list:
           raise HTTPException(status_code=404, detail="No post Found")
       return allpost_list 
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}")


@router.get("/postsbyUser/{user_id}")
def getPostById(user_id:int,db:Session=Depends(get_db),response_model= List[PostResponse]):   #Get post by Author ID
    try:
       posts=db.query(Post).filter_by(author_id=user_id).all()    
       if not posts:
           raise HTTPException(status_code=404,detail=f"Post not found")
       return posts
    except Exception as e:
        raise HTTPException(status_code= 500,detail=f"Internal server Error {str(e)}")
    

@router.get("/posts/{id}")
def getPostById(id:int,db:Session=Depends(get_db)):   #Get post by ID
    try:
        posts=db.query(Post, User.username).join(User, User.id == Post.author_id).filter(Post.id == id).first()
        if not posts:
            raise HTTPException(status_code=404,detail=f"Post not found")
        post,username =posts
        return { "id" : post.id, "title":post.title,"author_id":post.author_id,"img_url":post.img_url, "username" :username, "content": post.content,"created_at":post.created_at }
    except Exception as e:
        raise HTTPException(status_code= 500,detail=f"Internal server Error {str(e)}")
    
    
@router.post("/createPost")
def create_post(post:PostModel,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #Create Post   
    try:
        post_data=Post(**post.model_dump())
        post_data.author_id=current_user["id"] 
        db.add(post_data)
        db.commit()
        return {"status":"success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")
    
    
@router.put("/posts/{id}")
def update_post(id:int,post:PostUpdateModel,db:Session = Depends(get_db),current_user = Depends(token_validation)):  #update Post
   try:
    post_data=post.model_dump(exclude_unset=True)
    if post_data["author_id"]==current_user["id"]:
       db.query(Post).filter(Post.id==id).update(post_data)  
    else:
        raise HTTPException(status_code=403,detail=f"Not allowed to edit this post")   
    db.commit() 
    return {"status":"success"}
   except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")
   
 
@router.delete("/posts/{id}")
def delete_data(id: int, db: Session = Depends(get_db), current_user = Depends(token_validation)):
    try:
        post = db.query(Post).filter(Post.id == id).first()
        if not post:
            raise HTTPException(status_code=404,detail=f"Post not found {str(e)}")
        if post.author_id != current_user["id"]:
            raise HTTPException(403, "Not allowed")
        db.delete(post) 
        db.commit()
        return {"status": "success", "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")


