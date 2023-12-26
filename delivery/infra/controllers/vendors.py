# Author: CP

from infra.models import Vendors
from utils import hash
from utils import rolepolicy

def getAll():
    vendors = Vendors.objects.all()
    vendors = [v.asJson() for v in vendors]
    return {"vendors": vendors}

def createVendor(vendorDetails, billing, payload):
    vendor = Vendors(
        vendorDetails=vendorDetails,
        billing=billing,
        payload=payload
    )
    vendor.save()

    return vendor.asJson()

