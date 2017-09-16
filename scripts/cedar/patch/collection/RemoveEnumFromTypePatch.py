import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromTypePatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for a static template field"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['enum'\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties/@type$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": {
                "type": "string",
                "format": "uri"
            },
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
