import jsonpatch
import re
from cedar.patch import utils


class AddRdfsLabelToPropertiesPatch(object):

    def __init__(self):
        self.description = "Adds the missing rdfs:label in the properties object"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'rdfs:label'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
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
            "op": "add",
            "value": {
                "type": [
                    "string",
                    "null"
                ]
            },
            "path": path + "/rdfs:label"
        }]
        return jsonpatch.JsonPatch(patches)
