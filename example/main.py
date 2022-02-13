import network
import time
import ufirestore
from ufirestore.json import FirebaseJson

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect("ssid", "pass")
    print("Waiting for Wi-Fi connection", end="...")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print()

token = "INSERT_ACCESS_TOKEN"
ufirestore.set_project_id("INSERT_PROJECT_ID")
ufirestore.set_access_token(token)
raw_doc = ufirestore.get("DOCUMENT_PATH")
doc = FirebaseJson.from_raw(raw_doc)

if doc["fields"].exists("FIELD"):
    print("The field value is: %s" % doc["fields"].get("FIELD"))
