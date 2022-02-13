class FirebaseJson:
    def __init__(self, data={}):
        self.data = data

    def __getitem__(self, key):
        return FirebaseJson(self.data[key])

    @classmethod
    def to_value_type(cls, value):
        if value == None:
            typ = "nullValue"
        elif isinstance(value, bool):
            typ = "booleanValue"
        elif isinstance(value, int):
            typ = "integerValue"
        elif isinstance(value, float):
            typ = "doubleValue"
        elif value.startswith("/t"):
            typ = "timestampValue"
            value = value[2:]
        elif value.startswith("/r"):
            typ = "referenceValue"
            value = value[2:]
        elif value.startswith("/g"):
            typ = "geoPointValue"
            value = value[2:].split(",")
            value = {
                "latitude": value[0],
                "longitude": value[1]
            }
        elif isinstance(value, str):
            typ = "stringValue"
        elif isinstance(value, bytes):
            typ = "bytesValue"
        elif isinstance(value, list):
            typ = "arrayValue"
            return {typ: {"values": [cls.to_value_type(item) for item in value]}}
        elif isinstance(value, dict):
            typ = "mapValue"
            return {typ: {"fields": {k: cls.to_value_type(v) for k, v in value.items()}}}

        return {typ: str(value)}

    @classmethod
    def from_value_type(cls, value):
        typ = [k for k in value.keys()][0]
        if typ == "nullValue":
            return None
        elif typ == "booleanValue":
            return bool(value[typ])
        elif typ == "integerValue":
            return int(value[typ])
        elif typ == "doubleValue":
            return float(value[typ])
        elif typ == "timestampValue":
            return str(value[typ])
        elif typ == "referenceValue":
            return str(value[typ])
        elif typ == "stringValue":
            return str(value[typ])
        elif typ == "bytesValue":
            return bytes(value[typ])
        elif typ == "arrayValue":
            return [cls.from_value_type(item) for item in value[typ]["values"]]
        elif typ == "mapValue":
            return {k: cls.from_value_type(v) for k, v in value[typ]["fields"].items()}

    def cursor(self, path, cb):
        segments = path.split("/")
        cur = self.data
        for i, s in enumerate(segments):
            if i == len(segments) - 1:
                # If final segment is reached
                return cb(cur, s)
            elif s not in cur or not isinstance(cur[s], dict):
                cur[s] = dict()
            cur = cur[s]

    def set(self, path, value, as_type=False):
        def cb(cur, s):
            if as_type:
                cur[s] = self.to_value_type(value)
            else:
                cur[s] = value

        return self.cursor(path, cb)

    def get(self, path, default=None):
        def cb(cur, s):
            if default != None:
                return cur.get(s, default)

            return cur[s]

        return self.cursor(path, cb)

    def add(self, path, name, value):
        def cb(cur, s):
            cur[s].update({name: value})

        return self.cursor(path, cb)

    def add_item(self, path, value):
        def cb(cur, s):
            if s not in cur:
                cur[s] = []
            cur[s].append(value)

        return self.cursor(path, cb)

    def remove(self, path):
        def cb(cur, s):
            del cur[s]

        return self.cursor(path, cb)

    def exists(self, path):
        def cb(cur, s):
            return s in cur

        return self.cursor(path, cb)

    def process(self, name):
        return {
            "name": name,
            "fields": self.data
        }

    @classmethod
    def from_raw(cls, raw):
        fields = raw["fields"]
        doc_data = {
            "name": raw["name"],
            "createTime": raw["createTime"],
            "updateTime": raw["updateTime"]
        }
        doc_data.update(fields={k: cls.from_value_type(v)
                        for k, v in fields.items()})
        return FirebaseJson(doc_data)


class Query(FirebaseJson):
    OPERATIONS = {
        "<": "LESS_THAN",
        "<=": "LESS_THAN_OR_EQUAL",
        ">": "GREATER_THAN",
        ">=": "GREATER_THAN_OR_EQUAL",
        "==": "EQUAL",
        "!=": "NOT_EQUAL",
        "array-contains": "ARRAY_CONTAINS",
        "in": "IN",
        "array-contains-any": "ARRAY_CONTAINS_ANY",
        "not-in": "NOT_IN"
    }

    def __init__(self, *args, **kwargs):
        self.num_filters = 0
        super().__init__(*args, **kwargs)

    def from_(self, collection_id, all_descendants=False):
        self.add_item("from", {
            "collectionId": collection_id,
            "allDescendants": all_descendants
        })
        return self

    def select(self, field):
        self.add_item("select/fields", {
            "fieldPath": field
        })
        return self

    def order_by(self, field, direction="DESCENDING"):
        self.add_item("orderBy", {
            "field": {
                "fieldPath": field
            },
            "direction": direction
        })
        return self

    def limit(self, value):
        self.set("limit", value)
        return self

    def where(self, field, op, value):
        if op not in self.OPERATIONS:
            raise Exception("Invalid query operation: %s" % op)

        if self.num_filters == 1:
            cur_filter = self.get("where/fieldFilter")
            self.remove("where/fieldFilter")
            self.set("where/compositeFilter/op", "AND")
            self.add_item("where/compositeFilter/filters", cur_filter)
            self.add_item("where/compositeFilter/filters", {
                "field": {
                    "fieldPath": field
                },
                "op": self.OPERATIONS[op],
                "value": self.to_value_type(value)
            })
        else:
            self.set("where/fieldFilter/field/fieldPath", field)
            self.set("where/fieldFilter/op", self.OPERATIONS[op])
            self.set("where/fieldFilter/value", self.to_value_type(value))

        self.num_filters += 1
        return self

    def process(self):
        return self.data
