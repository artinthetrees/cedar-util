import jsonpatch
import re
from cedar.patch import utils


class RecreateElementRequiredPatch(object):

    def __init__(self):
        self.description = "Fixes the property list of the element's required array"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile(
            "array is too short: must have at least 2 elements but instance has \d elements at ((/properties/[^/]+/items)*(/properties/[^/]+)*)+/required$|" +
            "instance value \('.+'\) not found in enum \(possible values: \['.+'\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)+/required/\d+$")
        if pattern.match(error_description):
            path = utils.get_error_location(error_description)
            property_path = path[:path.rfind("/required")]
            property_object = utils.get_json_object(doc, property_path)
            if utils.is_template_element(property_object):
                return True
            else:
                return False
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = utils.get_error_location(error_description)

        property_path = path[:path.rfind("/required")]
        property_object = utils.get_json_object(doc, property_path)

        patches = [{
            "op": "remove",
            "path": property_path + "/required"
        },
        {
            "op": "add",
            "value": self.get_element_required_properties(property_object),
            "path": property_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)

    def get_element_required_properties(self, element_object):
        user_properties = self.get_user_properties(element_object.get("properties"))
        required_properties = [
            "@context",
            "@id"]  # mandatory property names
        required_properties.extend(user_properties)
        return required_properties

    @staticmethod
    def get_user_properties(properties_object):
        exclude_list = ["@context", "@id", "@type", "xsd", "schema", "pav", "oslc", "pav:createdOn",
                        "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy"]
        property_names = list(properties_object.keys())
        return [item for item in property_names if item not in exclude_list]
