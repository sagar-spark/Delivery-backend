# Author: CP

from utils import rolepolicy
from utils import response

class Auth:
    def __init__(self, get_response):
        self.get_response = get_response

        self.noAuthUrl = []
        self.authUrl = []

        self.nameToUrlMapping = {}
        self.urlToNameMapping = {}

        self.userRoles = {}
        self.userRolesMeta = {}


        # URLs Initialiser
        allUrls = rolepolicy.URLs.ALL_URLS
        for urlKey in allUrls:
            url = allUrls[urlKey]
            path = self.getPathFromUrl(url)
            self.nameToUrlMapping[urlKey] = path
            self.urlToNameMapping[path] = urlKey
            if "noauth" in url and url["noauth"]:
                self.noAuthUrl.append(path)
            else:
                self.authUrl.append(path)
        #print ("No Auth Urls: ", self.noAuthUrl)
        #print ("Auth Urls: ", self.authUrl)


        # Role Initialiser per user in the organisation
        for userTypeKey in rolepolicy.Role.ROLE_RIGHTS_MAPPING:
            userType = rolepolicy.Role.ROLE_RIGHTS_MAPPING[userTypeKey]
            self.userRoles[userTypeKey] = []

            # Same URLs across multiple rights will be handled with this set
            localSet = set()
            localSetMeta = set()
            for rights in userType["RIGHTS"]:
                rightsUrls = rolepolicy.Role.REP[rights]
                for urlName in rightsUrls:
                    localSet.add(self.nameToUrlMapping[urlName])
                    #localSetMeta.add(rolepolicy.URLs.ALL_URLS[urlName])
                    localSetMeta.add(urlName)
            for url in userType["URLS"]:
                localSet.add(self.nameToUrlMapping[url])
                #localSetMeta.add(rolepolicy.URLs.ALL_URLS[url])
                localSetMeta.add(url)
            self.userRoles[userTypeKey] = list(localSet)
            self.userRolesMeta[userTypeKey] = []
            for url in list(localSetMeta):
                self.userRolesMeta[userTypeKey].append({url: rolepolicy.URLs.ALL_URLS[url]})
        #print (self.userRoles)


    def getPathFromUrl(self, url):
        base = url["base"].split('.')[0]
        path = "/{}/{}".format(base, url["name"])
        return path


    # Function which is called when any endpoint is hit in Django app
    def __call__(self, request):
        
        bearerWord = "Bearer "
        auth = False
        requestPath = request.path
        receivedJwtToken = request.headers.get("Authorisation")
        if receivedJwtToken is None:
            receivedJwtToken = request.headers.get("Authorization")
        if receivedJwtToken is not None and bearerWord in receivedJwtToken:
            receivedJwtToken = receivedJwtToken.split(bearerWord)[1]
        if requestPath in self.noAuthUrl:
            auth = True
        else:
            # Check if the user has rights to make call to this path
            decodedToken = rolepolicy.verifyUserLoginToken(receivedJwtToken)
            # The following status means that the token is untampered and valid
            if decodedToken["status"]:
                js = { "userDetails": decodedToken["token"]["user"]}
                request.META.update(js)
                roles = {"userRoles": self.userRolesMeta}
                request.META.update(roles)
                callerRole = decodedToken["token"]["user"]["role"]
                if requestPath in self.userRoles[callerRole]:
                    auth = True
        auth = True
        if auth:
            resp = self.get_response(request)
            return resp
        else:
            obj = { "msg": "Unauthorised" }
            return response.error(request, obj, status=403)

