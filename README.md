# FastAPI EasyAuth #

## What is this? ##
This library quickly and easily creates authentication using JWT and Cookies. You can also use easyauth to identify an active user

### Communication with me
__If you want to point out inaccuracies, suggest an idea, or report an error, write to the mail tragglesocial@gmail.com__

### Using ###

> This is the option where you store the jwt token in cookies. There is a more convenient way to store it in a session.
> [Use the storage option in the session](#sessionauth)
> The section about storing jwt in a session is called **sessionauth**


First, we need to import the EasyAuth and Jwt classes from easyauth

    from fastapi_easyauth import EasyAuth, Jwt, ALGORITHM

After that, we create instances of classes
```python
jwt = Jwt(
    secret = "SECRET", # The secret key for generating tokens and decoding them. Keep the token secret
    algorithm = ALGORITHM.HS256 # The encryption algorithm
    model = MyModel # Your Pydantic model. When decoding the token, the result will be converted to this model
)

auth = EasyAuth(
    cookie_name = "user" # The Name Of The Cookie File
    jwt = jwt
    expires = exp.EXPIRES_30_DAYS # Cookie lifetime
    )
```

Great, everything is ready. Now we can create tokens and decode them. Also check if the user is active. 
```python
from fastapi import FastAPI, Request, Response, Depends
from fastapi_easyauth import EasyAuth, Jwt, ALGORITHM, exp

from pydantic import BaseModel

class User(BaseModel):
    name: str
    password: str

app = FastAPI()

jwt = Jwt(
    secret = "SECRET",
    algorithm = ALGORITHM.HS256
)

auth = EasyAuth(
    cookie_name = "user"
    jwt = jwt
    expires = exp.EXPIRES_30_DAYS
)

@app.post('/log')
def log(user: User, response: Response):
    token = jwt.create_token(user)
    auth.save_token_in_cookie(response, token)
    return {'status': 200}


@app.get('/active')
def active(user: User = Depends(auth.active_user))
    return user
```
----------
# sessionauth
# Storing a JWT token in a session
This is a new way to store jwt tokens. The token will now be stored in the session. For convenience, the SessionAuth class was created

### Before you start working with Session Auth in Fastape, you need to connect SessionMiddleware
```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key = 'secret-key')
```

# Using
First, we need to import the necessary classes.
```python
from fastapi_easyauth.sessionauth import SessionAuth
from fastapi_easyauth import Jwt
```
After that, we create instances of the Jwt and SessionAuth classes
```python
jwt = Jwt(
	'secret'
)

sessionauth = SessionAuth(
	jwt = jwt,
	name_in_session = 'session-auth' # our token will be stored under this name in the session
)
```

To create and save a token, you can use one or two functions
```python
from pydantic import BaseModel

class UserModel(BaseModel):
	id: int
	username: str


router = APIRouter()

@router.get('/login')
async def login(usermodel: UserModel, request: Request):
	token = sessionauth.create_token(subject = usermodel)
	sessionauth.save_token_in_session(token, request)
	
	#or
	
	sessionauth.create_and_save_token_in_session(
	subject = usermodel,
	request = request
)

  

@router.get('/active')
async def active(
active_user: UserModel = Depends(sessionauth.active_user)
):

	return active_user
```
The ```active_user``` function will return the active user. It will automatically decrypt the token and return the dictionary or Pydantic model. If there is no token, it returns False

# Checking if there is an authorized user
Sometimes we want to prevent unauthorized users from accessing our resources. The ```only_auth``` and ```async_only_auth``` decorators were created for this purpose. You must specify ```request: Request```
## How it works
We just need to wrap our endpoint in our decorator.
```python
@router.get('/something')
@only_auth
def something(request: Request): ...


@router.get('/something/async')
@async_only_auth
async def something_async(request: Request): ...
```
You must specify request: Request
```only_auth``` for synchronous endpoint, and ```async_only_auth``` for asynchronous endpoint

# Creating your own decorators
The ```OnlyAuthCreater``` class will help you to create your own decorators
First, we need to create an instance of the ```OnlyAuthCreater``` class.

```python
json_response = JSONResponse(
    content = {
        'detail': 'Access is closed to unauthorized users'
    },
    status_code = 401
)

creater = OnlyAuthCreater(
    redirect_url = 'http:127.0.0.1:8000/auth/login', # the user will be redirected to this url if he is not logged in.
    response = json_response, # this response will be returned if the user is not logged in
    sessionauth = sessionauth # an instance of the SessionAuth class
)

only_auth_decorator_redirect = creater.create_only_auth_decorator() # Creating a decorator that will redirect the user to a specific url (which you specified when initializing the OnlyAuthCreater class)
only_auth_decorator_response = creater.create_only_auth_decorator(response = True) # Creating a decorator that will return a JSON response (we specified this response when initializing the OnlyAuthCreater class)

async_only_auth_decorator_redirect = creater.create_async_only_auth_decorator() # Asynchronous version. Redirect to a specific url
async_only_auth_decorator_response = creater.create_async_only_auth_decorator(response = True) # Asynchronous version. Returns a JSON response
```
Now the decorators you have created can be used
```python
@router.get('/test')
@only_auth_decorator_redirect
def test(request: Request): ...

@router.get('/test')
@only_auth_decorator_response
def test(request: Request): ...


@router.get('/test')
@async_only_auth_decorator_redirect
async def test(request: Request): ...

@router.get('/test')
@async_only_auth_decorator_response
async def test(request: Request): ...
```

## What is the RequestNotAdded error?
This error appears for one simple reason. For the ```only_auth```, ```async_auth``` and ```OnlyAuthCreater``` decorators to work, you need a request sent to your endpoint. To solve this problem, you need to add the ```request: Request``` function to your endpoint parameters. This is the only way to work for decorators.
Exemple:
```python

# Wrong! You need to specify in the endpoint request
@router.get('/something/async')
@async_only_auth
async def something_async(): ...

# Wrong. This is not the correct name for Request. Be sure to specify the name of the request
@router.get('/something/async')
@async_only_auth
async def something_async(req: Request): ...

# Success!
@router.get('/something/async')
@async_only_auth
async def something_async(request: Request): ...
```
---

# What was added and changed in version 0.1.0 #

+ Now, using only an instance of the EasyAuth class, you can create a token and immediately save it in a cookie.

```python
@app.post('/login')
def login(user: User, response: Response):
    token = auth.create_token(subject = user, response = response)
    return token

@app.get('/getToken')
def get_token(request: Request):
    data = auth.decode_token(request)
    return data
```

+ The name of the Auth class has also been changed to EasyAuth.
+ All functions have been documented
+ Now, when initializing the Jwt class, you can specify the model. Each time you decode the token, the result will be returned in the form of the model that you specified

```python
class User(BaseModel):
    id: int
    username: str

jwt = Jwt(
    secret = "SECRET",
    model = User
)


def get_user(token: str) -> User:
    # if you did not specify the model during initialization, the result will be returned as a dictionary
    
    user = jwt.decode_token(token)
    return user


def get_user_in_model(token: str) -> User:
    # If you are not going to add models when initializing the Jwt class, then you can use the decode_taken_in_model function.
    # It accepts a token and a model in which
    
    user = jwt.decode_token_in_model(token, User)
    return user
```

----------
### There are also two simple functions in this library so far. The first is password hashing. The second is an error about an unauthorized user. ###

```python
def hash_password(password: str) -> str:
    """
    hash_password: hashes the password

    Args:
        password (str): User password

    Returns:
        str: hashed password
    """

    return hashlib.sha256(password.encode()).hexdigest()


def not_authorized() -> HTTPException:
    """
    not_authorized: a function that returns an error when an unauthorized user
    """

    return HTTPException(
        status_code=401,
        detail='Unauthorized'
    )
```

### What was added or changed in version 0.2.1
- A new way of storing the Jwt token has been added. It can now be stored in a session. The SessionAuth class has been added to work with sessions
- Added new decorators ```only_auth``` and ```async_only_auth```. The goal is to return a JSON response if the user is not logged in, otherwise endpoint works
- The ```OnlyAuthCreater``` class has been added. This class creates custom decorators. You can decide which JSON response will be returned to the unauthorized user. Or redirect the user to another link
