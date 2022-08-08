import base64
import logging
import sys
import time
import urllib

import requests
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from requests import HTTPError
from logging import Logger

class SSOException(Exception):
    def __init__(self, message):
        self.message = message


class EveSSO(object):

    logger : Logger = None
    client_id : str = None
    app_secret : str = None
    callbackUrl : str = None
    character_id : str= None
    character_name : str= None
    access_token : str= None
    refresh_token : str= None
    token_expiry : int = None

    def __init__(self, client_id, app_secret, callbackUrl, scope_list):
        """init the Eve ESI helper class

        Args:
            client_id : app client id in your eve portal
            app_secret : app secret key in your eve portal
            callbackUrl : Call back URL for OATH2
            scope_list : Scope of EVE you want granted in a list
        """
        self.logger = logging.getLogger("eveapi")
        self.client_id = client_id
        self.app_secret = app_secret
        self.callbackUrl = callbackUrl

        self.code_verifier = "sander sso"
        if isinstance(scope_list, list):
            self.scopes = " ".join(scope_list)
        else:
            raise AttributeError("scope_list must be a list of scope.")

    def get_auth_url(self, code_challenge=None):
        """Prints the URL to redirect users to.

        Args:
            code_challenge: A PKCE code challenge
        """

        base_auth_url = "https://login.eveonline.com/v2/oauth/authorize/"
        params = {
            "response_type": "code",
            "redirect_uri": self.callbackUrl,
            "client_id": self.client_id,
            "scope": self.scopes,
            # "scope": "esi-characters.read_blueprints.v1",
            "state": "unique-state",
        }

        if code_challenge:
            params.update(
                {"code_challenge": code_challenge, "code_challenge_method": "S256"}
            )

        string_params = urllib.parse.urlencode(params)
        full_auth_url = "{}?{}".format(base_auth_url, string_params)
        self.logger.debug("authentification URL : {}".format(full_auth_url))
        return full_auth_url

    def callbackLoggin(self, auth_code):
        ret = None
        res = self.__send_token_request(auth_code)
        try:
            res.raise_for_status()
        except HTTPError as e:
            self.logger.debug(
                "Fail to get token, SSO response code is: {}".format(
                    sso_response.status_code
                )
            )
            self.logger.debug(
                "Fail to get token, SSO response JSON is: {}".format(
                    sso_response.json()
                )
            )
            raise SSOException("unable to log Eve")
        else:
            ret = self.__handle_sso_token_response(res)
        return ret

    def __send_token_request(self, auth_code):
        """Sends a request for an authorization token to the EVE SSO.

        Args:
            auth_code : the authorization code from the callback URL
        Returns:
            requests.Response: A requests Response object
        """
        user_pass = "{}:{}".format(self.client_id, self.app_secret)
        basic_auth = base64.urlsafe_b64encode(user_pass.encode("utf-8")).decode()
        auth_header = "Basic {}".format(basic_auth)

        form_values = {
            "grant_type": "authorization_code",
            "code": auth_code,
        }

        add_headers = {"Authorization": auth_header}

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        }

        if add_headers:
            headers.update(add_headers)

        res = requests.post(
            "https://login.eveonline.com/v2/oauth/token",
            data=form_values,
            headers=headers,
        )

        self.logger.debug(
            "__send_token_request :: Request to get token sent to URL {} with headers {} and form values: "
            "{}".format(res.url, headers, form_values)
        )

        return res

    def __store_token(self, jwt, access_token, refresh_token, expires_in):
        self.character_id = jwt["sub"].split(":")[2]
        self.character_name = jwt["name"]
        self.access_token = access_token
        self.token_expiry = int(time.time()) + expires_in
        self.logger.info("\nSuccess! log to Eve")

    def __handle_sso_token_response(self, sso_response):
        """Handles the authorization code response from the EVE SSO.

        Args:
            sso_response: A requests Response object gotten by calling the EVE
                        SSO /v2/oauth/token endpoint
        """

        if sso_response.status_code == 200:
            data = sso_response.json()
            access_token = data["access_token"]
            refresh_token = ""
            if "refresh_token" in data:
                refresh_token = data["refresh_token"]
            expires_in = data["expires_in"]

            self.logger.debug("\nVerifying access token JWT...")
            jwt = self.__validate_eve_jwt(access_token)

            self.__store_token(jwt, access_token, refresh_token, expires_in)

            headers = {"Authorization": "Bearer {}".format(access_token)}

            blueprint_path = (
                "https://esi.evetech.net/latest/characters/{}/"
                "blueprints/".format(self.character_id)
            )

            res = requests.get(blueprint_path, headers=headers)
            # print("\nMade request to {} with headers: "
            #      "{}".format(blueprint_path, res.request.headers))
            res.raise_for_status()

            data = res.json()
            return "{} has {} blueprints".format(self.character_name, len(data))
        else:
            self.logger.debug(
                "Request ko : Sent request with url: {} \nbody: {} \nheaders: {}".format(
                    sso_response.request.url,
                    sso_response.request.body,
                    sso_response.request.headers,
                )
            )
            self.logger.debug(
                "SSO response code is: {}".format(sso_response.status_code)
            )
            self.logger.debug("SSO response JSON is: {}".format(sso_response.json()))

    def __validate_eve_jwt(self, jwt_token):
        """Validate a JWT token retrieved from the EVE SSO.

        Args:
            jwt_token: A JWT token originating from the EVE SSO
        Returns
            dict: The contents of the validated JWT token if there are no
                validation errors
        """

        jwk_set_url = "https://login.eveonline.com/oauth/jwks"

        res = requests.get(jwk_set_url)
        try:
            res.raise_for_status()
        except HTTPError as e:
            self.logger.debug(
                "https://login.eveonline.com/oauth/jwks erreur : {}".format(res.reason)
            )
            raise SSOException("loggin failed, invalid JWT Token")

        data = res.json()

        try:
            jwk_sets = data["keys"]
        except KeyError as e:
            self.logger.debug(
                "Something went wrong when retrieving the JWK set. The returned "
                "payload did not have the expected key {}. \nPayload returned "
                "from the SSO looks like: {}".format(e, data)
            )
            raise SSOException("loggin failed, invalid JWT Token")

        jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))

        try:
            return jwt.decode(
                jwt_token,
                jwk_set,
                algorithms=jwk_set["alg"],
                issuer=("login.eveonline.com", "https://login.eveonline.com"),
                audience="EVE Online",
            )
        except ExpiredSignatureError:
            print("The JWT token has expired: {}")
            sys.exit(1)
        except JWTError as e:
            print("The JWT signature was invalid: {}").format(str(e))
            sys.exit(1)
        except JWTClaimsError as e:
            try:
                return jwt.decode(
                    jwt_token,
                    jwk_set,
                    algorithms=jwk_set["alg"],
                    issuer=("login.eveonline.com", "https://login.eveonline.com"),
                    audience="EVE Online",
                )
            except JWTClaimsError as e:
                print(
                    "The issuer claim was not from login.eveonline.com or "
                    "https://login.eveonline.com: {}".format(str(e))
                )
                sys.exit(1)

    def is_token_expired(self, offset=0):
        """Return true if the token is expired.
        The offset can be used to change the expiry time:
        - positive value decrease the time (sooner)
        - negative value increase the time (later)
        If the expiry is not set, always return True. This case allow the users
        to define a security object, only knowing the refresh_token and get
        a new access_token / expiry_time without errors.
        :param offset: the expiry offset (in seconds) [default: 0]
        :return: boolean true if expired, else false.
        """
        if self.token_expiry is None:
            return True
        return int(time.time()) >= (self.token_expiry - offset)

    def create_refresh_token(self, scope_list=None):
        """refresh the token if expire
        Args:
            scope_list: Socpe list as define in Eve key, if none get the old one in token
        """

        # 1 Prepare the header
        auth_b64 = "%s:%s" % (self.client_id, self.secret_key)
        auth_b64 = base64.b64encode(auth_b64.encode("utf-8"))
        auth_b64 = auth_b64.decode("utf-8")
        ath_header = {"Authorization": "Basic %s" % auth_b64}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        }
        headers.update(ath_header)

        # 2 prepare the params
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        if scope_list != None:
            if isinstance(scope_list, list):
                scopes = "+".join(scope_list)
            else:
                raise AttributeError("scope_list must be a list of scope.")
            params["scope"] = scopes

        # 3 make request
        res = requests.post(
            "https://login.eveonline.com/v2/oauth/token",
            data=form_values,
            headers=headers,
        )
        try:
            sso_response.raise_for_status()
        except HTTPError as e:
            self.logger.debug(
                "Fail to get token, SSO response code is: {}".format(
                    sso_response.status_code
                )
            )
            self.logger.debug(
                "Fail to get token, SSO response JSON is: {}".format(
                    sso_response.json()
                )
            )
            raise SSOException("unable to refresh token")

        # 4 verify JWT
        data = sso_response.json()
        access_token = data["access_token"]
        refresh_token = None
        if "refresh_token" in data:
            refresh_token = data["refresh_token"]
        expires_in = data["expires_in"]

        self.logger.debug("\nVerifying access token JWT with the refresh...")
        jwt = self.__validate_eve_jwt(access_token)

        # store the token
        self.__store_token(jwt, access_token, refresh_token, expires_in)

    def loadFromEveToken(
        self, access_token, refresh_token, token_expiry, character_name, character_id
    ):

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.character_name = character_name
        self.character_id = character_id
        return not self.is_token_expired()
