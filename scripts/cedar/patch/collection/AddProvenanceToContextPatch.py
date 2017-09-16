import jsonpatch
import re
from cedar.patch import utils


class AddProvenanceToContextPatch(object):

    def __init__(self):
        self.description = "Fixes the missing provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the @context object of a template"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/@context$")
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
                "@type": "@id"
            },
            "path": path + "/oslc:modifiedBy"
        },
        {
            "op": "add",
            "value": {
                "@type": "@id"
            },
            "path": path + "/pav:createdBy"
        },
        {
            "op": "add",
            "value": {
                "@type": "xsd:dateTime"
            },
            "path": path + "/pav:createdOn"
        },
        {
            "op": "add",
            "value": {
                "@type": "xsd:dateTime"
            },
            "path": path + "/pav:lastUpdatedOn"
        }]
        return jsonpatch.JsonPatch(patches)
