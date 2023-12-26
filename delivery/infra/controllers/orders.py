# Author: CP

import random

from datetime import datetime

from infra.models import Orders, OrdersMovementTable
from utils import hash
from utils import rolepolicy
from uuid import uuid4

def getAllGeoLocations(orderId):
    try:
        orderMovement = OrdersMovementTable.objects.get(orderId=orderId)
        return orderMovement.asJson()
    except OrdersMovementTable.DoesNotExist as e:
        err = { "msg": "Order Id does not exist in Movement Table" }
        return err

def updateGeoMilestone(orderId, name):
    try:
        print ("Updating")
        orderMovement = OrdersMovementTable.objects.get(orderId_id=orderId)
        milestone = {
            "path": orderMovement.geoLocations,
            "name": name,
            "datetime": datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        print (milestone)
        orderMovement.geoLocations = []
        orderMovement.milestone.append(milestone)
        print (orderMovement.geoLocations)
        print (orderMovement.milestone)
        orderMovement.save()
        return
    except OrdersMovementTable.DoesNotExist as e:
        err = { "msg": "Order Id does not exist in Movement Table" }
        return err

def updateGeoLocation(orderIds, user, latitude=None, longitude=None):
    if latitude is None or longitude is None:
        orderMovement = OrdersMovementTable(
            orderId_id=orderIds[0],
            geoLocations=[],
            milestone=[]
        )
        orderMovement.save()
        return 
    try:
        for orderId in orderIds:
            orderMovement = OrdersMovementTable.objects.get(orderId=orderId)
            if user["id"] == orderMovement.currentUser_id:
                locObj = [
                    latitude,
                    longitude,
                    datetime.now().strftime("%d-%m-%Y %H:%M"),
                    orderMovement.currentUser_id
                ]
                print (locObj)
                orderMovement.geoLocations.append(locObj)
                print (orderMovement.geoLocations)
                orderMovement.save()
        return
    except OrdersMovementTable.DoesNotExist as e:
        err = { "msg": "Order Id does not exist in Movement Table" }
        return err

def getDeliveryAgentPayload(deliveryUserId):
    obj = {
        "user": deliveryUserId,
        "datetime": datetime.now().strftime("%d-%m-%Y %H:%M")
    }
    return obj

def getStatusPayload(status, user):
    obj = {
        "status": status,
        "user": user,
        "datetime": datetime.now().strftime("%d-%m-%Y %H:%M")
    }
    return obj

def assignDeliveryAgentToOrder(orderId, deliveryUserId, user):
    try:
        status = "DELIVERY AGENT ASSIGNED"
        order = Orders.objects.get(id=orderId)
        newStatusPayload = getStatusPayload(status, user["id"])
        if order.currentUser_id == deliveryUserId:
            err = { 'msg': "Already assigned to the given agent" }
            return err
        order.currentUser_id = deliveryUserId
        order.status = "AGENT ASSIGNED"

        orderMovement = OrdersMovementTable.objects.get(orderId=order)
        orderMovement.currentUser_id = deliveryUserId
        orderMovement.save()

        order.usersHistory.append(getDeliveryAgentPayload(deliveryUserId))
        order.statusHistory.append(newStatusPayload)
        order.save()
        return order.asJson()
    except Orders.DoesNotExist as e:
        err = { "msg": "Order Id does not exist" }
        return err
    except Exception as e:
        err = {"msg": str(e)}
        return err

def createReceiverPayload(receiverDetails):
    key = str(uuid4()).replace('-', '')
    l = list(key)
    random.shuffle(l)
    key = ''.join(l)[0:6]
    obj = {"otp": key}
    return obj

def giveOrderFeedback(orderId, feedbackType, rating):
    try:
        err = {'msg': 'Rating already provided'}
        order = Orders.objects.get(id=orderId)
        if feedbackType == 'receiver':
            if order.userRating is not None:
                return err
            else:
                order.userRating = rating
                order.save()
                return order.asJson()
        if feedbackType == 'deliveryUser':
            if order.receiverRating is not None:
                return err
            else:
                order.receiverRating = rating
                order.save()
                return order.asJson()
    except Orders.DoesNotExist as e:
        err = { "msg": "Order Id does not exist" }
        return err

def updateOrderStatus(status, orderId, user):
    try:
        order = Orders.objects.get(id=orderId)
        if order.status == status:
            err = { "msg": "Order already assigned {} status".format(status) }
            return err
        order.status = status
        newStatusPayload = getStatusPayload(status, user["id"])
        order.statusHistory.append(newStatusPayload)
        order.save()
        return order.asJson()
    except Orders.DoesNotExist as e:
        err = { "msg": "Order Id does not exist" }
        return err

def createOrder(payload, user):
    vendorId = None
    userId = None
    userId = user["id"]
    dumpPayload = payload["payload"] if "payload" in payload else {}
    if user["role"] == rolepolicy.Role.ROLE_VENDOR:
        vendorId = user["vendorId"]
    else:
        vendorId = payload["vendorId"]
    order = Orders(
        pickLocation=payload["pickLocation"],
        dropLocation=payload["dropLocation"],
        vendorId_id=vendorId,
        currentUser=None,
        usersHistory=[],
        status="CREATED",
        statusHistory=[getStatusPayload("CREATED", userId)],
        auditHistory=None,
        receiverDetails=payload["receiverDetails"],
        receiverKey=payload["receiverKey"],
        receiverPayload=createReceiverPayload(payload["receiverKey"]),
        userRating=None,
        receiverRating=None,
        payload=dumpPayload
    )
    order.save()
    updateGeoLocation([order.id], None, None)

    return order.asJson()

def getAllOrders(vendorId, userId=None, orderId=None, shipmentId=None, status=None):
    orders = []
    filters = {}
    filtersInitialised = False

    if status is not None:
        filters["status__in"] = status
        filtersInitialised = True
    if shipmentId is not None:
        filters["shipmentId"] = shipmentId
        filtersInitialised = True
    if orderId is not None:
        filters["id"] = orderId
        filtersInitialised = True
    if vendorId is not None:
        filters["vendorId_id"] = vendorId
        filtersInitialised = True
    if userId is not None:
        filters["currentUser_id"] = userId
        filtersInitialised = True
    if not filtersInitialised:
        orders = Orders.objects.all()
    else:
        orders = Orders.objects.filter(**filters)
    orders = [order.asJson() for order in orders]
    return { "orders": orders }

