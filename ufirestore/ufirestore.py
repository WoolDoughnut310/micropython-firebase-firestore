import ujson
import _thread
import urequests

class FirestoreException(Exception):
    def __init__(self, message, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.message}"


class FIREBASE_GLOBAL_VAR:
    GLOBAL_URL_HOST = "https://firestore.googleapis.com"
    GLOBAL_URL_ADINFO = {
        "host": "https://firestore.googleapis.com", "port": 443}
    PROJECT_ID = None
    DATABASE_ID = "(default)"
    ACCESS_TOKEN = None
    SLIST = {}


def construct_url(resource_path=None):
    path = "%s/v1/projects/%s/databases/%s/documents" % (
        FIREBASE_GLOBAL_VAR.GLOBAL_URL_HOST, FIREBASE_GLOBAL_VAR.PROJECT_ID, FIREBASE_GLOBAL_VAR.DATABASE_ID)

    if resource_path:
        path += "/"+resource_path

    return path


def to_url_params(params=dict()):
    return "?" + "&".join(
        [(str(k) + "=" + str(v)) for k, v in params.items() if v is not None])


def get_resource_name(url):
    return url[url.find("projects"):]


def send_request(path, method="GET", params=dict(), data=None, dump=True):
    headers = {}
    if FIREBASE_GLOBAL_VAR.ACCESS_TOKEN:
        headers["Authorization"] = "Bearer " + FIREBASE_GLOBAL_VAR.ACCESS_TOKEN
    if method == "POST":
        response = urequests.request(method, path, data=None, json=data)
    else:
        response = urequests.request(method, path, headers=headers)

    if dump == True:
        if response.status_code < 200 or response.status_code > 299:
            print(response.text)
            raise FirestoreException(response.reason, response.status_code)

        jsonResponse = response.json()
        if jsonResponse.get("error"):
            error = json["error"]
            code = error["code"]
            message = error["message"]
            raise FirestoreException(message, code)
        return jsonResponse


class INTERNAL:

    def patch(DOCUMENT_PATH, DOC, cb, update_mask=None):
        PATH = construct_url(DOCUMENT_PATH)
        LOCAL_PARAMS = to_url_params()
        if update_mask:
            for field in update_mask:
                LOCAL_PARAMS += "updateMask=" + field
        DATA = DOC.process()
        LOCAL_OUTPUT = send_request(PATH, "POST", data=DATA)
        if cb:
            try:
                return cb(LOCAL_OUTPUT)
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return LOCAL_OUTPUT

    def create(COLLECTION_PATH, DOC, cb, document_id=None):
        PATH = construct_url(COLLECTION_PATH)
        PARAMS = {"documentId": document_id}
        DATA = DOC.process(get_resource_name(PATH))
        LOCAL_OUTPUT = send_request(PATH, "POST", PARAMS, DATA)
        if cb:
            try:
                return cb(LOCAL_OUTPUT)
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return LOCAL_OUTPUT

    def get(DOCUMENT_PATH, cb, mask=None):
        PATH = construct_url(DOCUMENT_PATH)
        LOCAL_PARAMS = to_url_params()
        if mask:
            for field in mask:
                LOCAL_PARAMS += "mask.fieldPaths=" + field
        LOCAL_OUTPUT = send_request(PATH+LOCAL_PARAMS, "GET")
        if cb:
            try:
                return cb(LOCAL_OUTPUT)
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return LOCAL_OUTPUT

    def getfile(DOCUMENT_PATH, FILENAME, cb, mask=None):
        PATH = construct_url(DOCUMENT_PATH)
        LOCAL_PARAMS = to_url_params()
        if mask:
            for field in mask:
                LOCAL_PARAMS += "mask.fieldPaths=" + field
        LOCAL_OUTPUT = send_request(PATH+LOCAL_PARAMS, "get")

        with open(FILENAME, "wb") as LOCAL_FILE:
            ujson.dump(LOCAL_OUTPUT, LOCAL_FILE)

        if cb:
            try:
                return cb(FILENAME)
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return FILENAME

    def delete(RESOURCE_PATH, cb):
        PATH = construct_url(RESOURCE_PATH)
        send_request(PATH, "DELETE")
        if cb:
            try:
                return cb(True)
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return True

    def list(COLLECTION_PATH, cb, page_size=None, page_token=None, order_by=None, mask=None, show_missing=None):
        PATH = construct_url(COLLECTION_PATH)
        LOCAL_PARAMS = to_url_params({
            "pageSize": page_size,
            "pageToken": page_token,
            "orderBy": order_by,
            "showMissing": show_missing
        })
        if mask:
            for field in mask:
                LOCAL_PARAMS += "mask.fieldPaths=" + field
        LOCAL_OUTPUT = send_request(PATH+LOCAL_PARAMS, "get")
        if cb:
            try:
                return cb(LOCAL_OUTPUT.get("documents"),
                          LOCAL_OUTPUT.get("nextPageToken"))
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return (LOCAL_OUTPUT.get("documents"), LOCAL_OUTPUT.get("nextPageToken"))

    def list_collection_ids(DOCUMENT_PATH, cb, page_size=None, page_token=None):
        PATH = construct_url(DOCUMENT_PATH)+":listCollectionIds"
        DATA = {
            "pageSize": page_size,
            "pageToken": page_token
        }
        LOCAL_OUTPUT = send_request(PATH, "POST", data=DATA)
        if cb:
            try:
                return cb(LOCAL_OUTPUT.get("collectionIds"),
                          LOCAL_OUTPUT.get("nextPageToken"))
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return (LOCAL_OUTPUT.get("collectionIds"),
                LOCAL_OUTPUT.get("nextPageToken"))

    def run_query(DOCUMENT_PATH, query, cb):
        PATH = construct_url(DOCUMENT_PATH)+":runQuery"
        DATA = {
            "structuredQuery": query.data
        }
        LOCAL_OUTPUT = send_request(PATH, "POST", data=DATA)
        if cb:
            try:
                return cb(LOCAL_OUTPUT.get("document"))
            except:
                raise OSError(
                    "Callback function could not be executed. Try the function without ufirestore.py callback.")
        return LOCAL_OUTPUT.get("document")


def set_project_id(id):
    FIREBASE_GLOBAL_VAR.PROJECT_ID = id


def set_access_token(token):
    FIREBASE_GLOBAL_VAR.ACCESS_TOKEN = token


def set_database_id(id="(default)"):
    FIREBASE_GLOBAL_VAR.DATABASE_ID = id


def patch(PATH, DOC, update_mask=None, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.patch, [PATH, DOC, cb, update_mask])
    else:
        return INTERNAL.patch(PATH, DOC, cb, update_mask)


def create(PATH, DOC, document_id=None, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.create, [PATH, DOC, cb, document_id])
    else:
        return INTERNAL.create(PATH, DOC, cb, document_id)


def get(PATH, mask=None, bg=False, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.get, [PATH, cb, mask])
    else:
        return INTERNAL.get(PATH, cb, mask)


def getfile(PATH, FILENAME, mask=None, bg=False, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.getfile, [PATH, FILENAME, cb, mask])
    else:
        return INTERNAL.getfile(PATH, FILENAME, cb, mask)


def delete(PATH, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(INTERNAL.delete, [PATH, cb])
    else:
        return INTERNAL.delete(PATH, cb)


def list(PATH, page_size=None, page_token=None, order_by=None, mask=None, show_missing=None, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.list, [PATH, cb, page_size, page_token, order_by, mask, show_missing])
    else:
        return INTERNAL.list(PATH, cb, page_size,
                             page_token, order_by, mask, show_missing)


def list_collection_ids(PATH, page_size=None, page_token=None, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.list_collection_ids, [PATH, cb, page_size, page_token])
    else:
        return INTERNAL.list_collection_ids(PATH, cb, page_size, page_token)


def run_query(PATH, query, bg=True, cb=None):
    if bg:
        _thread.start_new_thread(
            INTERNAL.run_query, [PATH, query, cb])
    else:
        return INTERNAL.run_query(PATH, query, cb)

