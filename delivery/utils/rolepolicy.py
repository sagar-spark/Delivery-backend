# Author: CP

import jwt
import traceback

from datetime import datetime, timedelta
from utils import env

class URLs:

    INFRA_MODULE = "infra.views"

    ALL_URLS = {
        "URL_ORDER_GETGEOMOVEMENTS": {
            "base": INFRA_MODULE,
            "name": "getAllGeoLocations",
            "label": "Get All Geo Movements"
        },
        "URL_ORDER_ADDGEOMILESTONE": {
            "base": INFRA_MODULE,
            "name": "updateGeoMilestone",
            "label": "Update Geo Milestone"
        },
        "URL_ORDER_ADDGEOLOCATION": {
            "base": INFRA_MODULE,
            "name": "updateGeoLocation",
            "label": "Update Geo Location"
        },
        "URL_ORDER_SUBMITFEEDBACK": {
            "base": INFRA_MODULE,
            "name": "giveOrderFeedback",
            "label": "Give Order Feedback"
        },
        "URL_ORDER_GETMOVEMENTS": {
            "base": INFRA_MODULE,
            "name": "getOrderMovements",
            "label": "Get Order Movements"
        },
        "URL_ORDER_UPDATESTATUS": {
            "base": INFRA_MODULE,
            "name": "updateOrderStatus",
            "label": "Update Order Status"
        },
        "URL_ORDER_ASSIGNDELIVERYAGENET": {
            "base": INFRA_MODULE,
            "name": "assignDeliveryAgentToOrder",
            "label": "Assign Delivery Agent"
        },
        "URL_ORDER_CANCEL": {
            "base": INFRA_MODULE,
            "name": "cancelOrder",
            "label": "Cancel Order"
        },
        "URL_ORDER_GETALL": {
            "base": INFRA_MODULE,
            "name": "getAllOrders",
            "label": "Get All Orders"
        },
        "URL_ORDER_CREATE": {
            "base": INFRA_MODULE,
            "name": "createOrder",
            "label": "Create Order"
        },
        "URL_GET_ALL_URLS": {
            "base": INFRA_MODULE,
            "name": "getallurls",
            #"noauth": True
        },
        "URL_SUPERADMIN_USER_SIGNUP": {
            "base": INFRA_MODULE,
            "name": "superadminusersignup",
            "label": "Super Admin Signup",
            "noauth": True
        },
        "URL_USER_GETALL": {
            "base": INFRA_MODULE,
            "name": "usergetall",
            "label": "Users"
        },
        "URL_USER_SIGNUP": {
            "base": INFRA_MODULE,
            "name": "usersignup",
            "label": "User Signup"
        },
        "URL_LOGIN_USER": {
            "base": INFRA_MODULE,
            "name": "userlogin",
            "label": "User Login",
            "noauth": True
        },
        "URL_FORGOT_PASSWORD_MAIL": {
            "base": INFRA_MODULE,
            "name": "forgotPasswordEmail",
            "label": "Forgot Password Mail",
            "noauth": True
        },
        "URL_RESET_PASSWORD": {
            "base": INFRA_MODULE,
            "name": "resetPassword",
            "label": "Reset Password",
            "noauth": True
        },
        "URL_CHANGE_PASSWORD": {
            "base": INFRA_MODULE,
            "name": "changePassword",
            "label": "Change Password",
        },
        
        "URL_VENDOR_ONBOARDING": {
            "base": INFRA_MODULE,
            "name": "vendorsignup",
            "label": "Vendor Signup"
        },
        "URL_VENDOR_GETALL": {
            "base": INFRA_MODULE,
            "name": "vendorgetall",
            "label": "Get All Vendors"
        }
    }

class Role:

    ROLE_DELIVERY   = 0
    ROLE_USER       = 1
    ROLE_MANAGER    = 2
    ROLE_ADMIN      = 3
    ROLE_SUPERADMIN = 4
    ROLE_VENDOR     = 5

    ROLE_CHOICES = (
        (ROLE_DELIVERY, "DELIVERY"), (ROLE_USER, "USER"),
        (ROLE_MANAGER, "MANAGER"), (ROLE_ADMIN, "ADMIN"),
        (ROLE_SUPERADMIN, "SUPERADMIN"), (ROLE_VENDOR, "VENDOR")
    )

    # Explicitly define admins so filters can be avoided
    ADMINS = [
        ROLE_SUPERADMIN, ROLE_ADMIN
    ]
    RESTRICTED_USER = [
        ROLE_DELIVERY
    ]

    # Rights with Endpoints
    REP = {
        "ROLE_DELIVERY_USERS": [
            "URL_ORDER_ADDGEOMILESTONE",
            "URL_ORDER_ADDGEOLOCATION",

            "URL_ORDER_SUBMITFEEDBACK",

            "URL_ORDER_UPDATESTATUS",
            "URL_ORDER_GETALL",

            "URL_GET_ALL_URLS",
            "URL_LOGIN_USER",
            "URL_FORGOT_PASSWORD_MAIL",
            "URL_RESET_PASSWORD",
            "URL_CHANGE_PASSWORD",
        ],
        "ROLE_MANAGER_USERS": [
            "URL_ORDER_GETGEOMOVEMENTS",
            "URL_ORDER_GETMOVEMENTS",
            "URL_ORDER_ASSIGNDELIVERYAGENET",
            "URL_ORDER_CANCEL",
            "URL_ORDER_GETALL",
            "URL_GET_ALL_URLS",
            "URL_LOGIN_USER",
            "URL_ORDER_CREATE",
            "URL_USER_GETALL",
            "URL_CHANGE_PASSWORD",

        ],
        "ROLE_ADMIN_USERS": [
            "URL_VENDOR_GETALL",
            "URL_VENDOR_ONBOARDING",
            "URL_LOGIN_USER",
            "URL_USER_SIGNUP",
            "URL_GET_ALL_URLS",
            "URL_ORDER_GETALL",
            "URL_ORDER_CANCEL",
            "URL_ORDER_ASSIGNDELIVERYAGENET",
            "URL_USER_GETALL",
            "URL_ORDER_CREATE",
            "URL_CHANGE_PASSWORD",
           
        ],
        "ROLE_VENDOR_USERS": [
            "URL_ORDER_GETMOVEMENTS",
            "URL_ORDER_CANCEL",
            "URL_ORDER_GETALL",
            "URL_ORDER_CREATE",
            "URL_GET_ALL_URLS",
            "URL_LOGIN_USER",
            "URL_CHANGE_PASSWORD",

        ],
        "ROLE_ORDERS_GEO": [
            "URL_ORDER_GETGEOMOVEMENTS",
            "URL_ORDER_ADDGEOMILESTONE",
            "URL_ORDER_ADDGEOLOCATION"
        ],
        "ROLE_ORDERS_MANAGE": [
            "URL_ORDER_SUBMITFEEDBACK",
            "URL_ORDER_GETMOVEMENTS",
            "URL_ORDER_UPDATESTATUS",
            "URL_ORDER_ASSIGNDELIVERYAGENET",
            "URL_ORDER_CANCEL",
            "URL_ORDER_GETALL",
            "URL_ORDER_CREATE"
        ],
    }

    ROLE_RIGHTS_MAPPING = {
        ROLE_DELIVERY: {
            "RIGHTS": [
                "ROLE_DELIVERY_USERS"
             ],
             "URLS": []
        },
        ROLE_USER: {
            "RIGHTS": [
            ],
            "URLS": []
        },
        ROLE_MANAGER: {
            "RIGHTS": [
                "ROLE_MANAGER_USERS"
            ],
            "URLS": []
        },
        ROLE_ADMIN: {
            "RIGHTS": [
                "ROLE_ADMIN_USERS"
            ],
            "URLS": []
        },
        ROLE_VENDOR: {
            "RIGHTS": [
                "ROLE_VENDOR_USERS"
            ],
            "URLS": []
        }
    }
    ROLE_RIGHTS_MAPPING[ROLE_SUPERADMIN] = { 
        #"RIGHTS": [ x for x in REP.keys()],
        "RIGHTS": [],
        "URLS": list(URLs.ALL_URLS.keys())
    }

def getUserLoginToken(user, expiry=None):
    jwtParams = { "user": user.asJson() }
    #jwtParams.update(Role.ROLE_RIGHTS_MAPPING[user.role])
    if expiry is not None and type(expiry) == int:
        jwtParams['exp'] = datetime.now() + timedelta(hours=expiry)

    token = jwt.encode(
        jwtParams,
        env.getEnvValue("JWT_SECRET"),
        algorithm="HS256"
    )
    return token

def verifyUserLoginToken(token):
    secret = env.getEnvValue("JWT_SECRET")
    retObject = {
        "status": False
    }
    if token is None:
        return retObject
    try:
        verifyToken = jwt.decode(
            token.encode(),
            secret,
            options={'verify_signature': True},
            algorithms=["HS256"]
        )
        retObject["token"] = verifyToken
        retObject["status"] = True
        return retObject
    except jwt.exceptions.ExpiredSignatureError as e:
        retObject["msg"] = str(e)
        return retObject
    except jwt.exceptions.DecodeError as e:
        retObject["msg"] = str(e)
        return retObject

