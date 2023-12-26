# Author: CP

from datetime import timedelta
from uuid import uuid4
from django.utils import timezone

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from delivery.utils.send_email import send_email

from infra.controllers import users
from infra.controllers import vendors
from infra.controllers import orders
from utils import rolepolicy
from utils import response
from .models import Users, ResetPasswordEmailLink

import json, traceback


def get_frontend_domain(request):
    if request:
        origin = request.headers.get('Origin')
        return origin
    else:
        # Replace with your actual domain
        return 'https://localhost:9009'   


@csrf_exempt
@require_http_methods(["GET"])
def usergetall(request):
    try:
        allUsers = users.usergetall()
        return response.success(request, {"users": allUsers})
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["GET"])
def getAllGeoLocations(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        orderMovement = orders.getAllGeoLocations(orderId)
        return response.success(request, orderMovement)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)

@csrf_exempt
@require_http_methods(["POST"])
def updateGeoMilestone(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        milestoneName = reqData["milestoneName"]
        orders.updateGeoMilestone(orderId, milestoneName)
        return response.success(request)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["POST"])
def updateGeoLocation(request):
    try:
        reqData = json.loads(request.body)
        orderIds = reqData["orderIds"]
        latitude = reqData["latitude"]
        longitude = reqData["longitude"]
        user = request.META["userDetails"]
        orders.updateGeoLocation(orderIds, user, latitude, longitude)
        return response.success(request)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["POST"])
def giveOrderFeedback(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        feedbackType = reqData["givenBy"]
        if feedbackType not in ["receiver", "deliveryUser"]:
            err = {'msg': 'Feedback can only be given by: receiver or deliveryUser'}
            return response.error(request, err)
        rating = reqData["rating"]
        if rating < 1 or rating > 5:
            err = {'msg': 'Allowed rating between 1 to 5'}
            return response.error(request, err)
        o = orders.giveOrderFeedback(orderId, feedbackType, rating)
        return response.success(request, o)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)

@csrf_exempt
@require_http_methods(["POST"])
def getOrderMovements(request):
    return response.success(request)

@csrf_exempt
@require_http_methods(["POST"])
def updateOrderStatus(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        status = reqData["status"]
        # TODO Handle Not Delivered
        # if status not in ["OUT FOR DELIVERY", "DELIVERED"]:
        #     err = {'msg': 'You are not allowed to update this status'}
        #     return response.error(request, err)
        user = request.META["userDetails"]
        o = orders.updateOrderStatus(status, orderId, user)
        return response.success(request)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)

@csrf_exempt
@require_http_methods(["POST"])
def assignDeliveryAgentToOrder(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        deliveryUserId = reqData["userId"]
        user    = request.META["userDetails"]
        o = orders.assignDeliveryAgentToOrder(orderId, deliveryUserId, user)
        return response.success(request, o)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["POST"])
def cancelOrder(request):
    try:
        reqData = json.loads(request.body)
        orderId = reqData["orderId"]
        user = request.META["userDetails"]
        o = orders.cancelOrder("CANCELLED", orderId, user)
        return response.success(request, o)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["GET"])
def getAllOrders(request):
    try:
        user = request.META["userDetails"]
        allOrders = None

        vendorId = None
        if "vendorId" in user:
            vendorId = user["vendorId"]

        userId = None
        if user["role"] in rolepolicy.Role.RESTRICTED_USER:
            userId = user["id"]

        params = request.GET
        orderId = int(params.get("orderId", default=0))
        orderId = None if orderId == 0 else orderId

        status = params.get("status", default=None)
        status = status.split(',') if status is not None else None

        shipmentId = params.get("shipmentId", default=None)

        allOrders = orders.getAllOrders(vendorId, userId, orderId, shipmentId, status)
        return response.success(request, allOrders)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["POST"])
def createOrder(request):
    try:
        reqData = json.loads(request.body)
        order = orders.createOrder(reqData, request.META["userDetails"])
        return response.success(request, order)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["GET"])
def getallurls(request):
    roles = request.META["userRoles"]
    user = request.META["userDetails"]
    obj = {"url": roles[user["role"]]}
    return response.success(request, obj)


@csrf_exempt
@require_http_methods(["GET"])
def vendorgetall(request):
    obj = vendors.getAll()
    return response.success(request, obj)

@csrf_exempt
@require_http_methods(["POST"])
def vendorsignup(request):
    try:
        reqData = json.loads(request.body)
        vendorDetails   = reqData["vendorDetails"]
        billing         = reqData["billing"]
        payload         = reqData["payload"]
        createUser      = reqData["createUser"]

        v = vendors.createVendor(
            vendorDetails=vendorDetails,
            billing=billing,
            payload=payload
        )

        u = None

        if createUser["yes"] == "yes":
            u = users.createUser(
                name=createUser["name"],
                email=createUser["email"],
                role=rolepolicy.Role.ROLE_VENDOR,
                password=createUser["password"]
            )

            v["user"] = u
        return response.success(request, v)
    except Exception as e:
        print (traceback.format_exc())
        err = {'msg': str(e)}
        return response.error(request, err)


@csrf_exempt
@require_http_methods(["POST"])
def superadminusersignup(request):
    try:
        reqData = json.loads(request.body)
        name = reqData['name']
        email = reqData['email']
        password = reqData['password']
        role = rolepolicy.Role.ROLE_SUPERADMIN
        u = users.createUser(
            name=name,
            email=email,
            role=role,
            password=password
        )
        return response.success(request, u)
    except Exception as e:
        err = { 'msg': str(e) }
        return response.error(request, err)

@csrf_exempt
@require_http_methods(["POST"])
def usersignup(request):
    try:
        reqData = json.loads(request.body)
        name = reqData['name']
        email = reqData['email']
        password = reqData['password']
        role = int(reqData['role'])
        payload = reqData["payload"]
        u = users.createUser(
            name=name,
            email=email,
            role=role,
            password=password,
            payload=payload
        )
        return response.success(request, u)
    except Exception as e:
        err = { 'msg': str(e) }
        return response.error(request, err)
    
@csrf_exempt
@require_http_methods(["POST"])
def forgotPasswordEmail(request):
    try:
        body = request.body
        request_data = json.loads(body)
        user = None
        user_email = request_data.get("email")
        user = Users.objects.filter(email=user_email).first()
                      
        if user:
            token = str(uuid4())
            # Set expiration time
            reset_link_created_at = timezone.now()
            setExpiryTimeForEmail(reset_link_created_at, user, token)

            # Send password reset email
            reset_url = f'{get_frontend_domain(request)}/#/pages/reset-password/{token}'
            
            send_link = send_email(request, user, reset_url)
            print(send_link)
            if send_link:
                message = 'Password reset link sent'
            else:
                message = "Could not send email."    
            return response.success(request, {'message': message})

        else:
            return response.error(request, {'message': 'Email Does Not Exist.'})
    except Exception as e:
        return response.error(request, {'message': e.args})

    
@csrf_exempt
@require_http_methods(["POST"])
def resetPassword(request):
    try:
        body = request.body
        request_data = json.loads(body)
        user = None
        new_password = request_data.get('password')
        token = request_data.get('token')
        # check if token is not expired
        expired = ResetPasswordEmailLink.objects.filter(
            token=token,
            expired_at__lt=timezone.now()
        ).first()

        reset_obj = ResetPasswordEmailLink.objects.filter(
                    token=token,
                ).first()
        if expired:
            return response.error(request, {'message': 'Link is expired. Please resend the mail.'}, status=400)
        elif not reset_obj:
            return response.error(request, {'message': 'Link is expired. Please resend the mail.'}, status=400)


        else:
            
            user = Users.objects.get(email=reset_obj.delievery_user.email)

           
        if user:
            user.hashed = False
            user.password = new_password
            user.save()
            reset_obj.delete()
            return response.success(request, {'message': 'Password changed successfully.'})    

    except Exception as e:
        return response.error(request, {"Error": e.args})


@csrf_exempt
@require_http_methods(["POST"])
def changePassword(request):
    print('here')
    try:
        body = request.body
        request_data = json.loads(body)
        user = request.META["userDetails"]
        old_password = request_data.get('oldPassword')
        new_password = request_data.get('newPassword')
        resp = users.updatePassword(old_password, new_password, user.get('email'))
        if resp:
            message = resp.get('resp')
        else:
            message = 'Unable to update password. Please try again.'
        return response.success(request, {'message': message})

    except Exception as e:
        return response.error(request, {"Error": e.args})



@csrf_exempt
@require_http_methods(["POST"])
def userlogin(request):
    try:
        header = request.headers.get("Content-Type")
        if header == "application/x-www-form-urlencoded":
            email = request.POST.get("client_id")
            password = request.POST.get("client_secret")
        else:
            reqData = json.loads(request.body)
            email = reqData['email']
            password = reqData['password']
        u = users.userLoginWithPassword(password, email)
        if u["status"]:
            return response.success(request, u)
        else:
            return response.error(request, u)
    except Exception as e:
        print (traceback.format_exc())
        err = { "msg": str(e) }
        return response.error(request, err)


def setExpiryTimeForEmail(reset_link_created_at, user, token):
    default_time_limit = 24

    expired_at = timezone.now() + timedelta(hours=default_time_limit)

    # Check the portal whether it is warehouse, admin, or vendor
    try:
        existing_link = ResetPasswordEmailLink.objects.get(delievery_user=user)
        existing_link.delete()
    except ResetPasswordEmailLink.DoesNotExist:
        pass

    ResetPasswordEmailLink.objects.create(
        delievery_user=user,
        created_at=reset_link_created_at,
        expired_at=expired_at,
        token=token
    )
    
