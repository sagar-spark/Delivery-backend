# Author: CP

from django.http import JsonResponse, HttpResponse

from uuid import uuid4

import json

def checkJson(resp):
    if resp is None or type(resp) != dict:
        raise Exception("Not a valid Json response")
    resp["respId"] = str(uuid4())

def logReqResp(request, response, status):
    obj = {
        "request": {
            "body": {},
            "headers": request.headers,
            "params": dict(request.GET),
        },
        "response": response,
        "id": response["respId"],
        "httpstatus": status,
        "method": request.method,
        "url": request.path
    }
    try:
        body = json.loads(request.body)
        obj["request"]["body"] = body
    except json.decoder.JSONDecodeError as e:
        pass
    print (obj)

def success(request, resp={}, status=200):
    checkJson(resp)
    logReqResp(request, resp, status)
    return JsonResponse(
        resp, status=status
    )

def error(request, resp={}, status=400):
    checkJson(resp)
    logReqResp(request, resp, status)
    return JsonResponse(
        resp, status=status
    )

