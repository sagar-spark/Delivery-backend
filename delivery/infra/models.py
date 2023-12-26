import pytz

from django.db import models

from uuid import uuid4

from utils import hash
from utils.rolepolicy import Role
from dateutil import parser


# Create your models here.

class OrdersMovementTable(models.Model):

    class Meta:
        app_label = "infra"
        constraints = [
            models.UniqueConstraint(
                fields=['orderId'],
                name='uniqueorderidinvendors'
            )
        ]

    id              = models.AutoField(primary_key=True)
    orderId         = models.ForeignKey(
        "Orders",
        on_delete=models.PROTECT,
    )
    geoLocations    = models.JSONField()
    milestone       = models.JSONField()
    currentUser     = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    created_ts  = models.DateTimeField(auto_now_add=True)
    updated_ts  = models.DateTimeField(auto_now=True)

    def asJson(self):
        obj = {
            "id": self.id,
            "currentUser": self.currentUser.asJson() if self.currentUser is not None else {},
            "orderId": self.orderId.id,
            "geoLocations": self.geoLocations,
            "milestone": self.milestone
        }

        return obj

class Orders(models.Model):

    class Meta:
        app_label = "infra"

    id              = models.AutoField(primary_key=True)
    shipmentId      = models.CharField(max_length=100)
    pickLocation    = models.JSONField()
    dropLocation    = models.JSONField()
    vendorId        = models.ForeignKey(
        "Vendors",
        on_delete=models.PROTECT
    )
    currentUser     = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    usersHistory    = models.JSONField()
    status          = models.CharField(max_length=100)
    # CREATED, AGENT ASSIGNED, OUT FOR DELIVERY, DELIVERED, NOT DELIVERED
    statusHistory   = models.JSONField()
    auditHistory    = models.JSONField(blank=True, null=True)

    receiverDetails = models.JSONField()    # Receiver Details that we dont care about
    receiverKey     = models.CharField(max_length=100) # Key to fetch Order Details
    receiverPayload = models.JSONField()    # Used to manage OTP and internal things
    userRating      = models.IntegerField(
        blank=True, null=True
    ) # 1-Bad, 2, 3, 4, 5- V Good; Given by Receiver
    receiverRating  = models.IntegerField(
        blank=True, null=True
    ) # 1-Bad, 2, 3, 4, 5- V Good; Given by User

    externalOrderReferenceId = models.CharField(max_length=100, blank=True, null=True) # External Order Reference Number so vendors can link their DB
    payload         = models.JSONField()

    created_ts  = models.DateTimeField(auto_now_add=True)
    updated_ts  = models.DateTimeField(auto_now=True)

    def asJson(self):
        
        obj = {
            "id": self.id,
            "shipmentId": self.shipmentId,
            "pickLocation": self.pickLocation,
            "dropLocation": self.dropLocation,
            "vendorId": self.vendorId.asJson(),
            "status": self.status,
            "statusHistory": self.statusHistory,
            "receiverDetails": self.receiverDetails,
            "receiverKey": self.receiverKey,
            "receiverPayload": self.receiverPayload,
            "payload": self.payload,
        }
        if self.currentUser is not None:
            obj["currentUser"] = self.currentUser.asJson()
        if self.usersHistory is not None:
            obj["usersHistory"] = self.usersHistory
        if self.auditHistory is not None:
            obj["auditHistory"] = self.auditHistory
        if self.userRating is not None:
            obj["userRating"] = self.userRating
        if self.receiverRating is not None:
            obj["receiverRating"] = self.receiverRating
        if self.statusHistory is not None and len(self.statusHistory) > 0:
            for entry in self.statusHistory:
                datetime_obj = parser.parse(entry["datetime"], dayfirst=True)
                # Convert the datetime object to ISO format
                formatted_datetime = datetime_obj.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
                # Update the "datetime" key in the entry with ISO formatted datetime
                entry["datetime"] = formatted_datetime


        return obj

    def save(self, *args, **kwargs):
        if self.shipmentId is None or self.shipmentId.strip() == "":
            self.shipmentId = str(uuid4()).upper().replace('-','')[:16]
        return super(Orders, self).save(*args, **kwargs)

class Vendors(models.Model):

    class Meta:
        app_label = "infra"
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='uniqueemailinvendors'
            )
        ]

    id              = models.AutoField(primary_key=True)
    email           = models.CharField(max_length=100)
    vendorDetails   = models.JSONField()
    billing         = models.JSONField()
    payload         = models.JSONField()

    created_ts  = models.DateTimeField(auto_now_add=True)
    updated_ts  = models.DateTimeField(auto_now=True)

    def asJson(self):
        obj = {
            "id": self.id,
            "email": self.email,
            "vendorDetails": self.vendorDetails,
            "billing": self.billing,
            "payload": self.payload,
        }
        return obj

class DeliveryUsersAttendance(models.Model):

    class Meta:
        app_label = "infra"

    id          = models.AutoField(primary_key=True)
    userId      = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT
    )
    checkInDateTime     = models.DateTimeField()
    checkOutDateTime    = models.DateTimeField()
    countOfDeliveries   = models.IntegerField()
    ordersServed        = models.JSONField()


class Users(models.Model):

    class Meta:
        app_label = "infra"
        ordering = ("name", )
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='uniqueemailinusers'
            )
        ]

    id          = models.AutoField(primary_key=True) 
    name        = models.CharField(max_length=100)
    email       = models.CharField(max_length=100)
    role        = models.IntegerField(choices=Role.ROLE_CHOICES)
    password    = models.CharField(max_length=100)
    hashed      = models.BooleanField(default=False)
    payload     = models.JSONField(blank=True, null=True)
    vendorId    = models.ForeignKey(
        "Vendors",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    # TODO: Add adhoc roles column

    created_ts  = models.DateTimeField(auto_now_add=True)
    updated_ts  = models.DateTimeField(auto_now=True)

    def asJson(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "payload": self.payload
        }
        if self.vendorId is not None:
            obj["vendorId"] = self.vendorId_id
        return obj

    def save(self, *args, **kwargs):
        self.password = self.password.strip()
        if self.password is None or self.password == "":
            return
        if self.hashed is False:
            digestPass = hash.getMd5Hash(self.password)
            self.password = digestPass
            self.hashed = True
 
        return super(Users, self).save(*args, **kwargs)

class ResetPasswordEmailLink(models.Model):
    delievery_user = models.OneToOneField(Users, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=False)
    expired_at = models.DateTimeField(auto_now_add=False)
    token = models.TextField()

    def __str__(self):
        return self.delievery_user.name