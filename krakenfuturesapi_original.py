import sys
import platform
import base64
import hashlib
import hmac

if int(platform.python_version_tuple()[0]) > 2:
    import urllib.request as urllib2
else:
    import urllib2

api_public = {"instruments", "tickers", "orderbook", "history"}
api_private_get = {"accounts", "openorders", "fills", "openpositions",
                   "transfers", "notifications", "historicorders", "recentorders"}
api_private_post = {"transfer", "sendorder", "cancelorder",
                    "cancelallorders", "cancelallordersafter", "batchorder", "withdrawal"}

api_domain = "https://futures.kraken.com/derivatives"
api_data = ""
8
if len(sys.argv) < 2:
    api_method = "instruments"
elif len(sys.argv) == 2:
    api_method = sys.argv[1]
else:
    api_method = sys.argv[1]
    for count in range(2, len(sys.argv)):
        if count == 2:
            api_data = sys.argv[count]
        else:
            api_data = api_data + "&" + sys.argv[count]

if api_method in api_private_get or api_method in api_private_post:
    api_path = "/api/v3/"
    try:
        api_key = open("Futures_Public_Key").read().strip()
        api_secret = base64.b64decode(
            open("Futures_Private_Key").read().strip())
    except:
        print("API key and API secret must be in text files called Futures_Public_Key and Futures_Private_key")
        sys.exit(1)
    api_postdata = api_data.encode('utf-8')
    api_sha256 = hashlib.sha256(
        api_postdata + api_path.encode('utf-8') + api_method.encode('utf-8')).digest()
    api_hmacsha512 = hmac.new(api_secret, api_sha256, hashlib.sha512)
    if api_method in api_private_get:
        api_request = urllib2.Request(
            api_domain + api_path + api_method + "?" + api_data)
    else:
        api_request = urllib2.Request(
            api_domain + api_path + api_method, api_postdata)
    api_request.add_header("APIKey", api_key)
    api_request.add_header(
        "Authent", base64.b64encode(api_hmacsha512.digest()))
    api_request.add_header("User-Agent", "Kraken Futures REST API")
elif api_method in api_public:
    api_path = "/api/v3/"
    api_request = urllib2.Request(
        api_domain + api_path + api_method + "?" + api_data)
    api_request.add_header("User-Agent", "Kraken Futures REST API")
else:
    print("Usage: %s method parameters" % sys.argv[0])
    print("Example: %s orderbook symbol=pi_xbtusd" % sys.argv[0])
    sys.exit(1)

try:
    api_reply = urllib2.urlopen(api_request).read().decode()
except Exception as error:
    print("API call failed due to unexpected error (%s)" % error)
    sys.exit(1)

if '"result":"success"' in api_reply:
    print(api_reply)
    sys.exit(0)
else:
    print(api_reply)
    sys.exit(1)
