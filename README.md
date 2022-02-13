# micropython-firebase-firestore

Firebase Firestore implementation for Micropython.

**Firebase implementation** based on [REST API](https://firebase.google.com/docs/firestore/reference/rest), based on [micropython-firebase-realtime-database](https://github.com/ckoever/micropython-firebase-realtime-database) from ckoever.

### Installation

You can use **uPip** to install library from **PyPi**

```python
import upip
upip.install("micropython-firebase-firestore")
```

or you can just upload `ufirestore/ufirestore.py` to your microcontroller:

```bash
python pyboard.py -d PORT -f cp ufirestore.py :
```

### Commands that are implemented

```
- set_project_id
- set_access_token
- patch
- create
- get
- getfile
- delete
- list
- list_collection_ids
- run_query
```

### Required modules

```
ujson, urequests, _thread
```

### Connect to Wifi

```python
import time
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect("ssid", "pass")
    print("Waiting for Wi-Fi connection", end="...")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print()
```

### Example Usage

Reads a field from a stored document

```python
import ufirestore

ufirestore.set_project_id("INSERT_PROJECT_ID")
ufirestore.set_access_token("INSERT_ACCESS_TOKEN")
raw_doc = ufirestore.get("DOCUMENT_PATH")
doc = FirebaseJson.from_raw(raw_doc)

if doc["fields"].exists("FIELD"):
    print("The field value is: %s" % doc["fields"].get("FIELD"))
```

The project ID is required, read about it [here](https://firebase.google.com/docs/projects/learn-more#project-id)
or you can find it at `Project Settings > General` in your project's [console](https://console.firebase.google.com)
The access token is obtained from the Firebase Auth API, which can be harnessed with my [auth library](https://github.com/WoolDoughnut310/micropython-firebase-auth), or reading can be done [here](https://firebase.google.com/docs/firestore/use-rest-api#authentication_and_authorization)

## Functions

### set_project_id

```python
ufirestore.set_project_id("INSERT_PROJECT_ID")
```

Set the ID of your Firebase project

### set_access_token

```python
ufirestore.set_access_token("INSERT_ACCESS_TOKEN")
```

Sets the access token to use for authentication

### patch

```python
ufirestore.patch(PATH, DOC, update_mask=[], bg=True, cb=None)
```

Updates or inserts a document `DOC` at the location `PATH`

-   Set the fields to update with `update_mask`
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
doc = FirebaseJson()
doc.set("age/integerValue", 21)

response = ufirestore.patch("users/234", doc, ["age"], False)
print(response)
```

### create

```python
ufirestore.create(PATH, DOC, document_id=None, bg=True, cb=None)
```

Creates a new document `DOC` at the collection at location `PATH`

-   `document_id` - The document ID to use for the document. If not specified, an ID will be generated
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
doc = FirebaseJson()
doc.set("name/stringValue", "Jane Doe")
doc.set("age/integerValue", 25)
doc.set("height/integerValue", 165)

response = ufirestore.create("users", doc, bg=False)
print(response)
```

### get

```python
ufirestore.get(PATH, mask=None, bg=True, cb=None)
```

Gets a single document at location `PATH`

-   `document_id` - The document ID to use for the document. If not specified, an ID will be generated
-   `mask` - The fields to return
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
response = ufirestore.get("users/129", bg=False)
doc = FirebaseJson.from_raw(response)

if doc.exists("fields/name"):
    print("Hello, %s" % doc.get("fields/name"))
```

### getfile

```python
ufirestore.getfile(PATH, FILENAME, mask=None, bg=True, cb=None)
```

Gets a single document at location `PATH` and writes it to file `FILENAME`

-   `document_id` - The document ID to use for the document. If not specified, an ID will be generated
-   `mask` - The fields to return
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
ufirestore.getfile("users/129", "user.json")
```

### delete

```python
ufirestore.delete(PATH, bg=True, cb=None)
```

Deletes a document at location `PATH`

-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
success = ufirestore.delete("users/129")

if success:
    print("User data successfully deleted.")
```

### list

```python
ufirestore.list(PATH, page_size=None, page_token=None, order_by=None, mask=None, show_missing=None, bg=True, cb=None)
```

Lists documents at location `PATH`

-   `page_size` - The number of documents to return
-   `page_token` - The `next_page_token` returned from a previous `list` option
-   `order_by` - The order to sort results by. For example: `priority desc, name`
-   `mask` - The fields to return. If not set, return all fields
-   `show_missing` - If the list should show missing documents
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
documents, next_page_token = ufirestore.list("users", bg=False)

for document in documents:
    doc = FirebaseJson.from_raw(document)
    if doc.exists("fields/age"):
        print("Age: %s" % doc.get("fields/age"))
```

### list_collection_ids

```python
ufirestore.list_collection_ids(PATH, page_size=None, page_token=None, bg=True, cb=None)
```

Lists all the collection IDs underneath a document at `PATH`

-   `page_size` - The maximum number of results to return
-   `page_token` - A page token
-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
collection_ids, next_page_token = ufirestore.list_collection_ids("rooms/28", bg=False)

for collection_id in collection_ids:
    print("ID: %s" % collection_id)
```

### run_query

```python
ufirestore.run_query(PATH, query, bg=True, cb=None)
```

Runs a query at location `PATH`

-   Optional run in the background with `bg`
-   Set a callback function after getting data with `cb`

#### Example

```python
from ufirestore.json import FirebaseJson, Query

query = Query().from_("users").where("age", ">=", 18)
raw_doc = ufirestore.run_query("", query, bg=False)
doc = FirebaseJson.from_raw(raw_doc)

if doc.exists("fields/name"):
    print("Resulted with user named %s" % doc.get("fields/name"))
```

## FirebaseJson

A simple helper class for Firebase document JSON data

### set

```python
doc.set(path, value, with_type=False)
```

Edit, overwrite or create new node at the specified path

-   `with_type` - If set to `True`, the value's type will be inferred and applied accordingly, as per a Firestore Document [Value](https://cloud.google.com/firestore/docs/reference/rest/v1/Value)

### get

```python
doc.get(path, default=None)
```

Get the node value at a given path, returning `default` if the path does not exist

### add

```python
doc.add(path, name, value)
```

Add a new node at the path, with name `name` and contents `value`

### add_item

```python
doc.add_item(path, value)
```

Adds an array item to the node at the path

### remove

```python
doc.remove(path)
```

Removes the node at the path

### exists

```python
doc.exists(path)
```

Checks whether a node exists at the path

### process

```python
doc.process(resource_name)
```

Processes json instance into a `dict` for usage with Firestore API

NOTE: All the functions in this library that require a document actually require the `FirebaseJon` instance and runs `process` behind the scenes

### FirebaseJson.from_raw

```python
FirebaseJson.from_raw(raw_doc)
```

Parses a raw document object from the Firestore API into a `FirebaseJson` instance

### Extra methods

### FirebaseJson.to_value_type

```python
FirebaseJson.to_value_type(value)
```

Infers the type of `value` and returns a `dict` in the format of a Firestore Document [Value](https://cloud.google.com/firestore/docs/reference/rest/v1/Value)

#### Example

```python
value = 35

data = FirebaseJson.to_value_type(value)

print(data) # Returns {"integerValue": "35"}
```

### FirebaseJson.from_value_type

```python
FirebaseJson.from_value_type(value)
```

Takes a Firestore Document [Value](https://cloud.google.com/firestore/docs/reference/rest/v1/Value) object and returns its value, casted to the correct type

#### Example

```python
# Example data from API
data = {
    "arrayValue": {
        "values": [
            {"stringValue": "a"},
            {"stringValue": "b"},
            {"integerValue": "3"}
        ]
    }
}

print(value) # Returns ["a", "b", 3]
```

## Query

Wrapper over `FirebaseJson` to easily create document queries

Extends all `FirebaseJson` methods

### from\_

```python
query.from_(collection_id, all_descendants=False)
```

-   `collection_id` - When set, selects only collections with this ID
-   `all_descendants` - When `True`, selects all descendant collections, when `False`, selects collections that are immediate children of the `parent` the query will be run on

### select

```python
query.select(field)
```

Adds a document field to return

### order_by

```python
query.order_by(field, direction="DESCENDING")
```

-   `field` - The field to order by
-   `direction` - The direction to order by (`ASCENDING` or `DESCENDING`)

### limit

```python
query.limit(value)
```

The maximum number of results to return, `value` must be >= 0

### where

```python
query.where(field, op, value)
```

Applies a filter on a specific field.

-   `field` - The field to filter by
-   `op` - The operation to filter by, is one of `<`, `<=`, `>`, `>=`, `==`, `!=`, `array-contains`, `in`, `array-contains-any`, `not-in`
-   `value` - The value to compare to, type is inferred with `FirebaseJson.to_value_type`

### process

```python
query.process()
```

Returns `dict` data of query for use with Firestore API

NOTE: This function is already used in the `run_query` function
