import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import getpass
import sys
import base64
import plistlib
import traceback
import json
import time


def getUDID(dsid, mmeFMFAppToken):
    url = 'https://p04-fmfmobile.icloud.com/fmipservice/friends/%s/1/maxCallback/refreshClient' % dsid
    headers = {
        # FMF APP TOKEN
        'Authorization': 'Basic %s' % base64.b64encode(("%s:%s" % (dsid, mmeFMFAppToken)).encode("utf-8")).decode("utf-8"),
        'Content-Type': 'application/json; charset=utf-8',
    }
    data = {
        "clientContext": {
            "appVersion": "5.0"
        }
    }
    jsonData = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(url, jsonData, headers)
    i = 0
    while 1:
        try:
            response = urllib.request.urlopen(request)
            break
        except:  # exception needs to be caught multiple times before request is complete
            i += 1
            continue
    x = json.loads(response.read())
    try:
        UDID = base64.b64decode(x["devices"][0]["id"].replace("~", "="))
        UDID = str(UDID, "utf-8")
    except Exception:
        # if we get any error, the user will have to manually confirm their UDID
        UDID = (False, False)
    return (UDID, x["devices"][0]["name"])


def tokenFactory(dsid, mmeAuthToken):
    mmeAuthTokenEncoded = base64.b64encode(
        ("%s:%s" % (dsid, mmeAuthToken)).encode("utf-8")).decode()
    # now that we have proper auth code, we will attempt to get all account tokens.
    url = "https://setup.icloud.com/setup/get_account_settings"
    headers = {
        'Authorization': 'Basic %s' % mmeAuthTokenEncoded,
        'Content-Type': 'application/xml',
        'X-MMe-Client-Info': '<iPhone6,1> <iPhone OS;9.3.2;13F69> <com.apple.AppleAccount/1.0 (com.apple.Preferences/1.0)>'
    }

    request = urllib.request.Request(url, None, headers)
    response = None
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code != 200:
            return "HTTP Error: %s" % e.code
        else:
            print(e)
            raise urllib.error.HTTPError

    content = response.read()
    mmeFMFAppToken = plistlib.loads(
        content)["tokens"]["mmeFMFAppToken"]
    return mmeFMFAppToken


def dsidFactory(uname, passwd):  # can also be a regular DSID with AuthToken
    creds = base64.b64encode(
        ("%s:%s" % (uname, passwd)).encode("utf-8")).decode("utf-8")
    url = "https://setup.icloud.com/setup/authenticate/%s" % uname
    headers = {
        'Authorization': 'Basic %s' % creds,
        'Content-Type': 'application/xml',
    }

    request = urllib.request.Request(url, None, headers)
    response = None
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code != 200:
            if e.code == 401:
                return "HTTP Error 401: Unauthorized. Are you sure the credentials are correct?"
            elif e.code == 409:
                return "HTTP Error 409: Conflict. 2 Factor Authentication appears to be enabled. You cannot use this script unless you get your MMeAuthToken manually (generated either on your PC/Mac or on your iOS device)."
            elif e.code == 404:
                return "HTTP Error 404: URL not found. Did you enter a username?"
            else:
                return "HTTP Error %s.\n" % e.code
        else:
            print(e)
            raise urllib.error.HTTPError
    content = response.read()
    DSID = int(plistlib.loads(content)[
               "appleAccountInfo"]["dsPrsID"])  # creating auth DSID
    mmeAuthToken = plistlib.loads(
        content)["tokens"]["mmeAuthToken"]  # creating token
    return (DSID, mmeAuthToken)


def convertAddress(street, city, state):
    street = street.replace(" ", "+")  # replace all spaces with a +
    city = city.replace(" ", "+")
    url = "http://maps.google.com/maps/api/geocode/json?address=%s,+%s+%s" % (
        street, city, state)
    headers = {
        'Content-Type': 'application/json',
    }
    request = urllib.request.Request(url, None, headers)
    response = None
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code != 200:
            return "HTTP Error: %s" % e.code
        else:
            print(e)
            raise urllib.error.HTTPError
    coords = json.loads(response.read())["results"][0]["geometry"]["location"]
    return (coords["lat"], coords["lng"])


def fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude):
    mmeFMITokenEncoded = base64.b64encode("%s:%s" % (DSID, mmeFMIToken))
    url = 'https://p04-fmip.icloud.com/fmipservice/findme/%s/%s/currentLocation' % (
        DSID, UDID)
    headers = {
        'Authorization': 'Basic %s' % mmeFMITokenEncoded,
        'X-Apple-PrsId': '%s' % DSID,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Accept-Language': 'en-us',
        'User-Agent': 'FMDClient/6.0 iPhone6,1/13F69',
        'X-Apple-Find-API-Ver': '6.0',
    }
    data = {
        "locationFinished": False,
        "deviceInfo": {
            "batteryStatus": "NotCharging",
            "udid": UDID,
            "batteryLevel": 0.50,
            "isChargerConnected": False
        },
        "longitude": longitude,
        "reason": 1,
        "horizontalAccuracy": 65,
        "latitude": latitude,
        "deviceContext": {
        },
    }
    jsonData = json.dumps(data)
    request = urllib.request.Request(url, jsonData, headers)
    try:
        urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code != 200:
            return "Error changing FindMyiPhone location, status code <%s>!" % e.code
        else:
            print(e)
            raise urllib.error.HTTPError
    return "Successfully changed FindMyiPhone location to <%s;%s>!" % (latitude, longitude)


def fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude):
    mmeFMFAppTokenEncoded = base64.b64encode(
        ("%s:%s" % (DSID, mmeFMFAppToken)).encode("utf-8")).decode("utf-8")
    url = 'https://p04-fmfmobile.icloud.com/fmipservice/friends/%s/%s/myLocationChanged' % (
        DSID, UDID)
    headers = {
        'host': 'p04-fmfmobile.icloud.com',
        'Authorization': 'Basic %s' % mmeFMFAppTokenEncoded,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'User-Agent': 'FindMyFriends/5.0 iPhone6,1/9.3.2(13F69)',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us',
        'X-Apple-Find-API-Ver': '2.0',
        'X-Apple-AuthScheme': 'Forever',
    }
    data = {
        "serverContext": {
            "authToken": "%s" % mmeFMFAppToken,
            "prsId": DSID,
        },
        "clientContext": {
            "appName": "FindMyFriends",  # need for proper server response
            "appVersion": "5.0",  # also need for proper server response
            "userInactivityTimeInMS": 5,
            "deviceUDID": "%s" % UDID,  # This is quite important.
            "location": {
                "altitude": 57,  # random number. can change.
                "longitude": "%s" % longitude,
                "source": "app",
                "horizontalAccuracy": 1.0,  # perfect horizontal accuracy.
                "latitude": "%s" % latitude,
                "speed": -1,
                "verticalAccuracy": 1.0  # perfect vertical accuracy.
            }
        }
    }
    jsonData = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(url, jsonData, headers)
    try:
        urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code != 200:
            return "Error changing FindMyFriends location, status code <%s>!" % e.code
        else:
            print(e)
            raise urllib.error.HTTPError
    return "Successfully changed FindMyFriends location to <%s;%s>!" % (latitude, longitude)


def poof(user, passw, latitude, longitude, duration):
    latitude = int(latitude)
    longitude = int(longitude)
    duration = int(duration)*60
    try:
        (DSID, authToken) = dsidFactory(user, passw)
        # print "Got DSID/MMeAuthToken [%s:%s]!" % (DSID, authToken) uncomment this if you want to see DSID and token
        print("Successfully authenticated to iCloud!")
    except:
        print("Error getting DSID and MMeAuthToken!\n%s" %
              dsidFactory(user, passw))
        sys.exit()
    serviceSelect = 0

    try:
        # get tokens by using token.
        mmeFMFAppToken = tokenFactory(DSID, authToken)
    except Exception as e:
        print("Error getting FMF/FMI tokens!\n%s" % e)  # 0 is the FMFAppToken
        traceback.print_exc()
        sys.exit()
    print("Attempting to find UDID's for devices on account.")
    UDID = getUDID(DSID, mmeFMFAppToken)
    if UDID[0] != False:
        print("Found UDID [%s] for device [%s]!" % (UDID[0], UDID[1]))
        confirm = "y"
        if confirm == "y" or confirm == "Y" or confirm == "yes" or confirm == "Yes":
            UDID = UDID[0]
        else:
            UDID = input("Okay, enter UDID manually: ")

    else:
        print("Could not get UDID for any device")
        UDID = input("UDID: ")

    try:
        counter = 0
        while counter < duration:
            if serviceSelect == 0 or serviceSelect == 1 or serviceSelect == 2:
                if serviceSelect == 0:  # do both
                    print(fmfSetLoc(DSID, mmeFMFAppToken,
                                    UDID, latitude, longitude))
                    print("Waiting 5 seconds to send FMF spoof again.")
                    time.sleep(5)
                    counter += 5
            else:
                print("Service select must have a value of 0, 1, or 2.")
                sys.exit()
    except KeyboardInterrupt:
        print("Terminate signal received. Stopping spoof.")
        print("Spoof stopped.")
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        sys.exit()
