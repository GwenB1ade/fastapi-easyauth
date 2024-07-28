from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from . import jwt
from functools import wraps

from typing import Union

class SessionAuth:
    
    def __init__(self, jwt: jwt.Jwt, name_in_session: str):
        """The Session Auth class is used to store the tokens in the session.
        This class helps the robot with creating tokens, storing tokens in a session, and verifying an active user.

        Args:
            jwt (jwt.Jwt)
            name_in_session (str): The jwt token will be stored in the session under this name
        """
        
        self.jwt = jwt
        self.name = name_in_session


    def create_token(self, subject: BaseModel):
        """Creating a jwt token

        Args:
            subject (BaseModel): The model by which the token will be created

        Returns:
            token (str): Jwt token
        """
        return self.jwt.create_token(subject)
    

    def save_token_in_session(self, token: str, request: Request):
        """Saving the jwt token in the session

        Args:
            token (str): Jwt token
            request (Request): FastAPI Request
        """
        request.session[self.name] = token


    def active_user(self, request: Request) -> Union[False, Union[dict, BaseModel]]:
        """Retrieves the token from the session and returns the decoded token. If there is no token, it returns False

        Args:
            request (Request): FastAPI Request

        Returns:
            Union[False, Union[dict, BaseModel]]: If there is no token in the session, then False, otherwise either the dictionary or the model
        """
        
        user = request.session.get(self.name)
        if user:
            return self.jwt.decode_token(user, full = False)
        
        else: return False
    
    
    def delete_token_from_session(self, request: Request):
        """Removes the token from the session

        Args:
            request (Request): FastAPI Request
        """
        request.session[self.name] = None
        
    
    def create_and_save_token_in_session(self, subject: BaseModel, request: Request):
        """Combining the create_token and save_token_in_session functions

        Args:
            subject (BaseModel): Pydantic Model
            request (Request): FastAPI Request
        """
        
        token = self.create_token(subject)
        self.save_token_in_session(token, request)
        
    
    def get_token_from_session(self, request: Request):
        """getting a token from a session

        Args:
            request (Request): FastAPI Request

        Returns:
            token (str): Jwt Token
        """
        token = request.session.get(self.name)
        return token

    
    
def unauthorized_json_response() -> JSONResponse:
    """This function returns a JSON response stating that the user is not logged in

    Returns:
        JSONResponse: FastAPI JSONResponse
    """
    return JSONResponse(
        content = {
            'detail': 'Unauthorized'
        },
        
        status_code = 401
    )


def only_auth(func):
    """Checks if the user is logged in, if not, returns the unauthorized_json_response function

    Args:
        func : Endpoint

    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            request = kwargs.get('request')
        
        except:
            class RequestNotAdded(Exception): ...
            raise RequestNotAdded('You forgot to add a request to your endpoint. Checking whether the user is authorized cannot be performed from the request. The required name is request')

        if SessionAuth.active_user(request) is False:
            return unauthorized_json_response()
        
        else:
            return func(*args, **kwargs)
        
    return wrapper


def async_only_auth(func):
    """Asynchronous version of the only_auth function

    Args:
        func : EndPoint

    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try: request = kwargs.get('request')
        
        except:
            class RequestNotAdded(Exception): ...
            raise RequestNotAdded('You forgot to add a request to your endpoint. Checking whether the user is authorized cannot be performed from the request. The required name is request')

        if SessionAuth.active_user(request) is False:
            return unauthorized_json_response()
        
        else:
            return await func(*args, **kwargs)

    
    return wrapper


class OnlyAuthCreater:
    """The class creates its own decorators to verify the authorized user"""
    
    def __init__(self, redirect_url: str, response: JSONResponse, sessionauth: SessionAuth):
        """_summary_

        Args:
            redirect_url (str): The link to redirect the user to if he is not logged in
            response (JSONResponse): JSON response if the user is not logged in
            sessionauth (SessionAuth): an instance of the SessionAuth class
        """
        self.re_url = redirect_url
        self.response = response
        self.auth = sessionauth
    
    
    def create_only_auth_decorator(self, response = False):
        """Creates a synchronous decorator.
        By default, in the created decorator, the response for an unauthorized user is a redirect, but if response = True, then the response is JSON.

        Args:
            response (bool, optional): If True, then in case of an unauthorized user, send a JSON response. Defaults to False.
        """
        def only_auth(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try: request = kwargs.get('request')
                except:
                    class RequestNotAdded(Exception): ...
                    raise RequestNotAdded('You forgot to add a request to your endpoint. Checking whether the user is authorized cannot be performed from the request. The required name is request')

                if self.auth.active_user(request) is False:
                    if response:
                        return self.response
                    
                    else:
                        return RedirectResponse(self.re_url)
                        
                
                else:
                    return func(*args, **kwargs)
                
            return wrapper
        
        return only_auth
    
    
    def create_async_only_auth_decorator(self, response = False):
        """Creates an asynchronous decorator
        By default, in the created decorator, the response for an unauthorized user is a redirect, but if response = True, then the response is JSON.

        Args:
            response (bool, optional): If True, then in case of an unauthorized user, send a JSON response. Defaults to False.
        """
        def async_only_auth(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try: request = kwargs.get('request')
                except:
                    class RequestNotAdded(Exception): ...
                    raise RequestNotAdded('You forgot to add a request to your endpoint. Checking whether the user is authorized cannot be performed from the request. The required name is request')
                
                if self.auth.active_user(request) is False:
                    if response:
                        return self.response
                    
                    else:
                        return RedirectResponse(self.re_url)
                
                else:
                    return await func(*args, **kwargs)

            
            return wrapper
        
        return async_only_auth