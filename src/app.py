import datetime
import logging
from logging.config import dictConfig

import firebase_admin
import flask_login
import google.auth.transport.requests
import google.oauth2.id_token
import requests
import requests_toolbelt.adapters.appengine
from firebase_admin import credentials, firestore
from flask import (Flask, json, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import LoginManager, current_user, login_required
from requests import HTTPError

from auth.loggin import User
from config.environnement import DevelopmentConfig
from config.logcfg import logger_config
from eveGateway.eveProxy import ProxyCaracter,EveGatewayCaching
from eveGateway.ssotools import EveSSO

from webconfig import myConfig

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
# requests_toolbelt.adapters.appengine.monkeypatch()


logging.config.dictConfig(logger_config)

app = Flask(__name__)
app.config.from_object(myConfig)
login_manager = LoginManager()
login_manager.init_app(app)
cred = credentials.Certificate("evetinyindustry-5946915108a7.json")
default_app = firebase_admin.initialize_app()
# flask_cors.CORS(app)
db = firestore.client()

client_id = "d792e8ee580b400c8dd9eebd3c468cce"
app_secret = "O3MQGGULEgVdfUAIycdJvGJ0b0MZu9AwlvVKUM8x"
callbackUrl = "http://localhost:8080/sso/callback"
eveScope = [
    "publicData",
    "esi-wallet.read_character_wallet.v1",
    "esi-characters.read_contacts.v1",
    "esi-characters.read_agents_research.v1",
    "esi-industry.read_character_jobs.v1",
    "esi-markets.read_character_orders.v1",
    "esi-characters.read_blueprints.v1",
]

eveGatewayCache = EveGatewayCaching()
# sso = EveSSO(app.config["ESI_CLIENT_ID"],app.config["ESI_SECRET_KEY"],callbackUrl,["publicData", "esi-wallet.read_character_wallet.v1", "esi-characters.read_contacts.v1", "esi-characters.read_agents_research.v1", "esi-industry.read_character_jobs.v1", "esi-markets.read_character_orders.v1", "esi-characters.read_blueprints.v1"])


@login_manager.user_loader
def load_user(user_id):
    user_ref = db.collection("utilisateurs").document(user_id)
    if user_ref != None:
        return User.get(user_id, user_ref)
    else:
        return None


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/home")
@login_required
def home():
    app.logger.debug("home - user UUID %s", format(current_user.get_id()))
    text = ""
    dUser_ref = current_user.get_data().get().to_dict()
    validToken = False
    # l'utilisateur n' jamais activé le sso à Eve
    if "access_token" in dUser_ref:
        sso: EveSSO = eveGatewayCache.getSso(current_user.get_id())
        if sso != None:
            sso: EveSSO = eveGatewayCache.getSso(current_user.get_id())
            validToken: bool = not sso.is_token_expired()
        else:
            sso = EveSSO(client_id, app_secret, callbackUrl, eveScope)
            validToken = sso.loadFromEveToken(
                dUser_ref["access_token"],
                dUser_ref["refresh_token"],
                dUser_ref["token_expiry"],
                dUser_ref["character_name"],
                dUser_ref["character_id"],
            )
            eveGatewayCache.AddCarater(current_user.get_id(), sso)

        app.logger.debug("home - token valid : %s", validToken)
        protraitUrl = ""
        if dUser_ref["access_token"] != None and validToken:

            headers = {"Authorization": "Bearer {}".format(sso.access_token)}

            blueprint_path = (
                "https://esi.evetech.net/latest/characters/{}/"
                "blueprints/".format(sso.character_id)
            )

            res = requests.get(blueprint_path, headers=headers)
            # print("\nMade request to {} with headers: "
            #      "{}".format(blueprint_path, res.request.headers))
            res.raise_for_status()

            data = res.json()
            text = "{} has {} blueprints".format(sso.character_name, len(data))
            personnage = ProxyCaracter(sso)
            protraitUrl = personnage.getPhotoUrl(personnage.PX64)
        return render_template(
            "home.html",
            text=text,
            dUser_ref=dUser_ref,
            ssoUrl=sso.get_auth_url(),
            ssoEve=sso,
            portrait=protraitUrl,
        )
    else:
        sso = EveSSO(client_id, app_secret, callbackUrl, eveScope)
        return render_template(
            "home.html", dUser_ref=dUser_ref, portrait="", ssoEve=sso
        )


@app.route("/login", methods=["GET", "POST"])
def servLogin():
    id_token = request.headers["Authorization"].split(" ").pop()
    app.logger.debug("\x1b[31;20m***********token google reçu***** %s\x1b[0m")
    user = User.loadFormToken(id_token)
    user_ref = db.collection("utilisateurs").document(user.get_id())
    if user_ref != None:
        user_ref.set({"lastLogin": datetime.datetime.now()}, merge=True)
    flask_login.login_user(user)
    data = {"message": "Done", "code": "SUCCESS"}
    return make_response(jsonify(data), 200)


@app.route("/sso/callback")
@login_required
def callback() :
    # l'utilisateur vient de se signer pour le SSO de Eve, on crée l'objet sso
    # on crontrole le token
    # on stole les infos en DB, pour les prochaines connexion
    # on cache les infos pour éviter le flood de requête DB
    sso = EveSSO(client_id, app_secret, callbackUrl, eveScope)
    auth_code = request.args.get("code")
    app.logger.debug("token app code  : %s", auth_code)
    user_id = current_user.get_id()
    ret = sso.callbackLoggin(auth_code)
   
    app.logger.debug("Callback -- Store token in DB --")
    app.logger.debug("Callback -- SSO Refresh  : %s", sso.refresh_token)
    app.logger.debug("Callback --  SSO access_token  : %s", sso.access_token)

        
    db.collection("utilisateurs").document(user_id).set(
        {
            "refresh_token": sso.refresh_token,
            "access_token": sso.access_token,
            "token_expiry": sso.token_expiry,
            "character_name": sso.character_name,
            "character_id": sso.character_id,
        },
        merge=True,
    )
    eveGatewayCache.AddCarater(current_user.get_id(), sso)
    return redirect(url_for("home"))

@app.route("/caracter")
@login_required
def caracterCard() : 
    dUser_ref : dict = current_user.get_data().get().to_dict()
    sso: EveSSO = eveGatewayCache.getSso(current_user.get_id())
    carac: ProxyCaracter = eveGatewayCache.getCaracter(current_user.get_id())
    return render_template(
            "caractereCard.html", dUser_ref=dUser_ref, portrait=carac.getPhotoUrl(),portrait2=carac.getPhotoUrl(carac.PX256), ssoEve=sso) 

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=myConfig.PORT, debug=True)
