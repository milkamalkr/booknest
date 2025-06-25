from fastapi import FastAPI


from routers import auth, me, subscription

app = FastAPI()


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(me.router, prefix="/users", tags=["Users"])
app.include_router(subscription.router, prefix="/users", tags=["Users"])

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}


# About page route
@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}


