import secrets
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware


class Nuclei(FastAPI):
    def __init__(
        self,
        *,
        title: str = "Nuclei",
        description: str = "Nuclei API",
        version: str = "0.1.0"
    ):
        """
        The function __init__() is a constructor that initializes the class NucleiAPI

        Arguments:

        * `title`: The title of your API.
        * `description`: A short description of the API.
        * `version`: str = "0.1.0"
        """

        super().__init__(title=title, description=description, version=version)
        self.add_models()
        self.add_routes()

    def configure_middlware(self):
        """
        It adds a middleware to the app
        """

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.add_middleware(SessionMiddleware, secret_key="hello world x0532")

    def add_routes(self):
        """
        It's a function that adds routes to the app
        """

        from nuclei_backend.users.main import users_router
        from nuclei_backend.storage_service.main import storage_service

        self.include_router(storage_service)

        self.include_router(users_router)

    def add_models(self):
        """
        It creates the tables in the database.
        """

        from .database import SessionLocal, engine
        from .storage_service import ipfs_model
        from .users import user_models

        user_models.Base.metadata.create_all(bind=engine)
        ipfs_model.Base.metadata.create_all(bind=engine)


app = Nuclei()
app.configure_middlware()
