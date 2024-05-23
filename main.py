from fastapi import FastAPI , Depends , HTTPException ,status,File, UploadFile , Response , Form , BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import EmailStr
from datetime import timedelta
from database import engine , get_db
from sqlalchemy.orm import Session
import schemas
import models 
import psycopg2
import Hash
import shutil
import os
import auth
from uuid import uuid4
from sendMail import send_email
from mailBody import body





app = FastAPI()


models.Base.metadata.create_all(bind=engine)


ACCESS_TOKEN_EXPIRE_MINUTES = 30



# app.include_router(posts.router)

@app.post("/register")
def register(request : schemas.CreateUser , db:Session = Depends(get_db)):
    if request.password == request.confirm_password:
        hashed =  Hash.hash_password(request.password)
        user = models.User(username = request.username , password = hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        return "user_registered"
    return "passwords are not matching"


@app.post("/login" , response_model=schemas.Token)
def login_page(request : schemas.User ,response : Response , db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not Hash.verify_password(request.password,user.password):
        return "invalid credentials"
     
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    response.set_cookie(key="token", value=access_token, httponly=True, secure=True, samesite='Strict')
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user








UPLOAD_DIRECTORY = "uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.get("/")
async def main():
    content = """
<body>
<form action="/upload" enctype="multipart/form-data" method="post">
<input name="text" type="text">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


def get_details(
    name: str = Form(...),
    rgdno: int = Form(...),
    email: EmailStr = Form(...),
    org: str = Form(...)
) -> schemas.Details:
    return schemas.Details(name=name, rgdno=rgdno, email=email, org=org)



@app.post("/upload")
async def upload_file(details: schemas.Details = Depends(get_details),
    file: UploadFile = File(...),db:Session = Depends(get_db)):
    user_id = str(uuid4())
    file_location = f"{UPLOAD_DIRECTORY}/{user_id}_{file.filename}" 
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    user = models.Registration(name=details.name ,user_id=user_id,rgdno=details.rgdno,email=details.email,org=details.org,approved=None)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

# current_user: schemas.User = Depends(auth.get_current_user )
@app.post("/admin/validate")
async def validate_user( data: schemas.AdminValidation,
                         background_tasks: BackgroundTasks,
                         db:Session = Depends(get_db)):
    user = db.query(models.Registration).filter(models.Registration.user_id==data.user_id).first()
    # if current_user != "admin":
    #     raise HTTPException(
    #         status_code=403,
    #         detail="You do not have the necessary permissions to access this resource",
    #     )
    if user.approved:
        return {"detail" : "User got already validated !"}
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.is_valid:
        username = f"user_{data.user_id[:8]}"
        password = f"pass_{data.user_id[:8]}"
        newUser = models.User(username=username,password=Hash.hash_password(password))
        remark = f"You are succesfully registered in Jivandeep. Your username : {username} and password : {password}. Kindly login to your account and change the credentials . ThankYOU!!"
        await send_email(background_tasks,{"email" : user.email,
            "subject" : "Successful registration in jivandeep.",
            "remark" : body(remark)}
            )
        user.approved=True
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
        return {"username": username, "password": password, "message": "User validated successfully"}
    else:
        user.approved=False
        db.commit()
        await send_email(background_tasks,{"email" : user.email,
                                           "subject" : "Registration unsuccessful.",
                                           "remark" : data.remark})
        return {"message": "User data invalid. Registration rejected."}

@app.post("/changePassword")
def change(request : schemas.passwordChange,current_user: schemas.User = Depends(auth.get_current_user) ,db:Session = Depends(get_db)):
    user=db.query(models.User).filter(models.User.username==request.username).first()
    user.password=request.password
    db.commit()

@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("token")
    return {"msg": "Successfully logged out"}