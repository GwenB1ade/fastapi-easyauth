import hashlib
from typing import Union, Optional
from fastapi import Depends, HTTPException, Request, Response, FastAPI
from pydantic import BaseModel
from . import exp
from .jwt import Jwt


def not_authorized() -> HTTPException:
    """
    not_authorized: a function that returns an error when an unauthorized user
    """

    raise HTTPException(
        status_code=401,
        detail='Unauthorized'
    )

class EasyAuth:

    def __init__(self, cookie_name: str, jwt: Jwt, expires: int = exp.EXPIRES_30_DAYS):
        """
        Args:
            cookie_name (str): the name of the cookie of the name in which the user's data will be stored
            jwt (Jwt): Jwt Object will encode and decode user data
            expires (int, optional): cookie lifetime. Defaults to exp.EXPIRES_30_DAYS.
        """

        self.cookie_name = cookie_name
        self.jwt = jwt
        self.expires = expires

    def active_user(self, request: Request, response: Response) -> Union[BaseModel, bool]:
        """
        active_user: checks if there is an active user, if not, it returns False, otherwise it returns the Pydantic model

        Args:
            request (Request): FastAPI Request
            response (Response): FastAPI Response

        Returns:
           Union[BaseModel, bool]: if the cookie has a token, it returns the User's model, otherwise False

        """

        token = request.cookies.get(self.cookie_name)
        if not token:
            return False

        user = self.jwt.decode_token(token, full=False)

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            expires=self.expires
        )

        return user

    def save_token_in_cookie(self, response: Response, token: str, expires: int = exp.EXPIRES_30_DAYS):
        """
        save_token_in_cookies: save token in cookies

        Args:
            response (Response): FastAPI Response
            token (str): User token
            expires (int, optional): cookie lifetime. Defaults to exp.EXPIRES_30_DAYS.
        """

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            expires=expires
        )

    def get_token(self, request: Request) -> str:
        """
        get_token: returns a token from a data cookie

        Args:
            request (Request): FastAPI Request

        Returns:
            str: User token
        """

        token = request.cookies.get(self.cookie_name)
        return token

    def decode_token(self, request: Request) -> Union[BaseModel, bool]:
        """
        decode_token: the function searches for a token in cookies, and then decodes the token into a model

        Args:
            request (Request): FastAPI Request

        Returns:
            Union[BaseModel, bool]: returns the user's model, or False
        """

        try:
            token = request.cookies.get(self.cookie_name)
            data = self.jwt.decode_token(token)
            return data

        except:
            return False

    def create_token(self, subject: BaseModel, response: Response) -> str:
        """
        create_token: encodes the model and creates a token, after which it stores the token in cookies

        Args:
            subject (BaseModel): The model to be encoded
            response (Response): FastAPI Response

        Returns:
            str: token
        """

        token = self.jwt.create_token(subject)
        response.set_cookie(self.cookie_name, token)
        return token
    
    def check_active_user(self, request: Request, response: Response, error = not_authorized):
        """
        check_active_user: checks if there is an active user, if not, returns an error

        Args:
            request (Request): FastAPI Request
            response (Response): FastAPI Response
            error (HTTPException, optional): the error that will be returned if the user is not logged in. Defaults to not_authorized().

        Usage Example:
        
            @router.get('/something', dependencies = [Depends(auth.check_active_user)])
            async def something_handler(request: Request): ...


        Returns:
            Union[BaseSchemas, dict]: the model or dict in which the user's data is recorded
        """
        
        user = self.active_user(request, response)
        if not user:
            raise HTTPException(status_code = 401, detail = 'Unauthorized')
        
        # return user


def hash_password(password: str) -> str:
    """
    hash_password: hashes the password

    Args:
        password (str): User password

    Returns:
        str: hashed password
    """

    return hashlib.sha256(password.encode()).hexdigest()



