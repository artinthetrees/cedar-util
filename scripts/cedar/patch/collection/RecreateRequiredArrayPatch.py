import jsonpatch
import re


class RecreateRequiredArrayPatch(object):

    def __init__(self):
        self.description = "Fixes the property list of a template's required array"
        self.since = "1.1.0"
        self.path = "/required"

    def is_applied(self, error_description):
        pattern = re.compile(
            "array is too short: must have at least 9 elements but instance has \d elements at /required$|" +
            "instance value \('.+'\) not found in enum \(possible values: \['.+'\]\) at /required/\d+$")
        if pattern.match(error_description):
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        properties_list = self.get_all_properties(doc)

        patches = []
        patch = {
            "op": "remove",
            "path": "/required"
        }
        patches.append(patch)
        patch = {
            "op": "add",
            "value": properties_list,
            "path": "/required"
        }
        patches.append(patch)

        return patches

    def get_all_properties(self, doc):
        default_properties = [
            "@context",
            "@id",
            "schema:isBasedOn",
            "schema:name",
            "schema:description",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]

        properties = list(doc["properties"].keys())
        for prop in properties:
            if prop not in default_properties:
                default_properties.append(prop)

        return default_properties