from datetime import timedelta
from fastapi_jwt import JwtAccessBearerCookie
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
import hashlib


class ALGORITHM:
    # DS Algorithms
    NONE = "none"
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"

    # Content Encryption Algorithms
    A128CBC_HS256 = "A128CBC-HS256"
    A192CBC_HS384 = "A192CBC-HS384"
    A256CBC_HS512 = "A256CBC-HS512"
    A128GCM = "A128GCM"
    A192GCM = "A192GCM"
    A256GCM = "A256GCM"

    # Pseudo algorithm for encryption
    A128CBC = "A128CBC"
    A192CBC = "A192CBC"
    A256CBC = "A256CBC"

    # CEK Encryption Algorithms
    DIR = "dir"
    RSA1_5 = "RSA1_5"
    RSA_OAEP = "RSA-OAEP"
    RSA_OAEP_256 = "RSA-OAEP-256"
    A128KW = "A128KW"
    A192KW = "A192KW"
    A256KW = "A256KW"
    ECDH_ES = "ECDH-ES"
    ECDH_ES_A128KW = "ECDH-ES+A128KW"
    ECDH_ES_A192KW = "ECDH-ES+A192KW"
    ECDH_ES_A256KW = "ECDH-ES+A256KW"
    A128GCMKW = "A128GCMKW"
    A192GCMKW = "A192GCMKW"
    A256GCMKW = "A256GCMKW"
    PBES2_HS256_A128KW = "PBES2-HS256+A128KW"
    PBES2_HS384_A192KW = "PBES2-HS384+A192KW"
    PBES2_HS512_A256KW = "PBES2-HS512+A256KW"

    # Compression Algorithms
    DEF = "DEF"

    HMAC = {HS256, HS384, HS512}
    RSA_DS = {RS256, RS384, RS512}
    RSA_KW = {RSA1_5, RSA_OAEP, RSA_OAEP_256}
    RSA = RSA_DS.union(RSA_KW)
    EC_DS = {ES256, ES384, ES512}
    EC_KW = {ECDH_ES, ECDH_ES_A128KW, ECDH_ES_A192KW, ECDH_ES_A256KW}
    EC = EC_DS.union(EC_KW)
    AES_PSEUDO = {A128CBC, A192CBC, A256CBC, A128GCM, A192GCM, A256GCM}
    AES_JWE_ENC = {A128CBC_HS256, A192CBC_HS384,
                   A256CBC_HS512, A128GCM, A192GCM, A256GCM}
    AES_ENC = AES_JWE_ENC.union(AES_PSEUDO)
    AES_KW = {A128KW, A192KW, A256KW}
    AEC_GCM_KW = {A128GCMKW, A192GCMKW, A256GCMKW}
    AES = AES_ENC.union(AES_KW)
    PBES2_KW = {PBES2_HS256_A128KW, PBES2_HS384_A192KW, PBES2_HS512_A256KW}

    HMAC_AUTH_TAG = {A128CBC_HS256, A192CBC_HS384, A256CBC_HS512}
    GCM = {A128GCM, A192GCM, A256GCM}

    SUPPORTED = HMAC.union(RSA_DS).union(EC_DS).union(
        [DIR]).union(AES_JWE_ENC).union(RSA_KW).union(AES_KW)

    ALL = SUPPORTED.union([NONE]).union(
        AEC_GCM_KW).union(EC_KW).union(PBES2_KW)

    HASHES = {
        HS256: hashlib.sha256,
        HS384: hashlib.sha384,
        HS512: hashlib.sha512,
        RS256: hashlib.sha256,
        RS384: hashlib.sha384,
        RS512: hashlib.sha512,
        ES256: hashlib.sha256,
        ES384: hashlib.sha384,
        ES512: hashlib.sha512,
    }


class Jwt:

    def __init__(self, secret: str, 
                 algorithm=ALGORITHM.HS256,
                 model: BaseModel = False,
                 auto_error: bool = True,
                 access_expires_delta: timedelta | None = None,
                 refresh_expires_delta: timedelta | None = None):
        """
        Args:
            secret (str): Your secret key, with which you can encode and decode tokens. Keep it a secret
            algorithm (_type_, optional): The encryption algorithm. All algorithms are in the jwt.py in the ALGORITHM class. Defaults to ALGORITHM.HS256.
            model (BaseModel, bool): Model. In the form of this model, the decoded result from the token will be returned. If False, the response will be returned by default
        """
        

        self.jwt = JwtAccessBearerCookie(
            secret_key=secret,
            algorithm=algorithm,
            auto_error = auto_error,
            access_expires_delta = access_expires_delta,
            refresh_expires_delta = refresh_expires_delta
        )
        
        self.model = False

        if type(model) == type(BaseModel):
            self.model = model

    def create_token(self, subject: BaseModel, expires_delta: timedelta = timedelta(hours = 1)) -> str:
        """
        create_token: the function encodes an object of the BaseModel type and creates a token

        Args:
            subject (BaseModel): the model of the BaseModel class. Located in pydantic

        Returns:
            str: token
        """
        token = self.jwt.create_access_token(
            subject=subject.dict(),
            expires_delta=timedelta,
        )

        return token

    def decode_token(self, token: str, full: bool = True) -> Union[BaseModel, dict]:
        """
        It is better not to use

        decode_token: the function decodes the token and returns the value

        Args:
            token (str): User token
            full (bool, optional): Determines whether to return the full or abbreviated response. If False,
                                    then only the dictionary with the decrypted model will be in the response. Defaults to True.

        Returns:
            Union[dict, BaseModel]: The answer is returned in the form of a dictionary.
                                    If you specified a model when initializing the class, the response will be returned in this model.
        """
        result = self.jwt._decode(token)

        if self.model:
            model = self.model.parse_obj(result.get('subject'))
            return model

        if full:
            return result

        else:
            return result.get('subject')

    def decode_token_in_model(self, token: str, model: BaseModel) -> BaseModel:
        """
        decode_token_in_model: the function decodes the token and converts the resulting value into a Pydantic model

        Args:
            token (str): User token
            model (BaseModel): Pydantic model. The result of token decoding will be converted into this model

        Returns:
            BaseModel: This is your model in which the decoded data is stored
        """

        result = self.jwt._decode(token).get('subject')

        result_model = model.parse_obj(result)
        return result_model


    def create_access_token(self,
                            subject: Dict[str, Any],
                            expires_delta: Optional[timedelta] = None,
                            unique_identifier: Optional[str] = None,):
        
        token = self.jwt.create_access_token(
            subject = subject,
            expires_delta = expires_delta,
            unique_identifier = unique_identifier
        )
        
        return token
    
    def create_refresh_token(self,
                        subject: Dict[str, Any],
                        expires_delta: Optional[timedelta] = None,
                        unique_identifier: Optional[str] = None,):
    
        token = self.jwt.create_refresh_token(
            subject = subject,
            expires_delta = expires_delta,
            unique_identifier = unique_identifier
        )
        
        return token
    
    
    def check_lifetime_token(self, token: str) -> bool:
        if self.jwt.auto_error == True:
            try:
                data = self.jwt._decode(token)
                return True
            
            except:
                return False
        
        data = self.jwt._decode(token)
        
        return True if data else False
        
        
    
    
    