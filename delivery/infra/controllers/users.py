# Author: CP

from infra.models import Users
from utils import hash
from utils import rolepolicy
from django.contrib.auth.hashers import check_password



def createUser(name, email, role, password, payload={}):
    user = Users(
        name=name,
        email=email,
        role=role,
        password=password,
        payload=payload
    )
    user.save()
    print (user.asJson())

    return user.asJson()

def usergetall():
    allUsers = Users.objects.all().exclude(role=rolepolicy.Role.ROLE_SUPERADMIN).exclude(role=rolepolicy.Role.ROLE_VENDOR)
    allUsers = [user.asJson() for user in allUsers]
    return allUsers


def updatePassword(oldPassword, newPassword, email=None):
    retObject = {
        "status": False,
        "resp": None
    }

    if email is None:
        retObject["resp"] = "Email is needed"
        return retObject 

    try:
        user = Users.objects.get(email=email)
        
        # Check if the old password matches
        if check_password(oldPassword, user.password):
            user.set_password(newPassword)
            user.save()
            retObject["resp"] = user.asJson()  
            retObject["status"] = True
        else:
            retObject['resp'] = 'Old password is not correct.'

    except Users.DoesNotExist as e:
        retObject["resp"] = "Email does not exist"

    return retObject


def userLoginWithPassword(password, email=None):
    retObject = {
        "status":False,
        "resp":None
    }
    if email is None:
        retObject["resp"] = "Email and password are needed"
        return retObject
    digest = hash.getMd5Hash(password)
    try:
        user = Users.objects.get(password=digest, email=email)
        token = rolepolicy.getUserLoginToken(user, expiry=24)
        retObject["status"] = True
        retObject["resp"] = token
        retObject["access_token"] = token
        retObject["client_id"] = email
        retObject["expires_in"] = 86400
        retObject["role"] = user.role
        return retObject
    except Users.DoesNotExist as e:
        retObject["resp"] = "Bad combination of username and password"
        retObject["status"] = False
        return retObject

