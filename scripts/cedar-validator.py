import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator, finder
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server",
                        choices=['local', 'staging', 'production'],
                        default="staging",
                        help="The type of CEDAR server")
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'instance'],
                        default="template",
                        help="The type of CEDAR resource")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="The maximum number of resources to validate")
    parser.add_argument("apikey", metavar="apiKey",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    server_address = get_server_address(args.server)
    type = args.type
    limit = args.limit
    api_key = args.apikey

    report = create_empty_report()

    if type == 'template':
        validate_template(api_key, server_address, limit, report)
    elif type == 'element':
        validate_element(api_key, server_address, limit, report)
    elif type == 'field':
        pass
    elif type == 'instance':
        validate_instance(api_key, server_address, limit, report)

    show(report)


def validate_template(api_key, server_address, limit, report):
    template_ids = get_template_ids(api_key, server_address, limit)
    total_templates = len(template_ids)
    for index, template_id in enumerate(template_ids, start=1):
        template = get_template(api_key, server_address, template_id)
        request_url = server_address + "/command/validate?resource_type=template"
        status_code, server_message = validator.validate_template(api_key, template, request_url=request_url)
        consume(report, template_id, status_code, server_message, iteration=index, total_count=total_templates)


def validate_element(api_key, server_address, limit, report):
    element_ids = get_element_ids(api_key, server_address, limit)
    total_elements = len(element_ids)
    for index, element_id in enumerate(element_ids, start=1):
        element = get_element(api_key, server_address, element_id)
        request_url = server_address + "/command/validate?resource_type=element"
        status_code, server_message = validator.validate_element(api_key, element, request_url=request_url)
        consume(report, element_id, status_code, server_message, iteration=index, total_count=total_elements)


def validate_instance(api_key, server_address, limit, report):
    instance_ids = get_instance_ids(api_key, server_address, limit)
    total_instances = len(instance_ids)
    for index, instance_id in enumerate(instance_ids, start=1):
        instance = get_instance(api_key, server_address, instance_id)
        request_url = server_address + "/command/validate?resource_type=instance"
        status_code, server_message = validator.validate_instance(api_key, instance, request_url=request_url)
        consume(report, instance_id, status_code, server_message, iteration=index, total_count=total_instances)


def get_element_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=element"
    return finder.all_templates(api_key, request_url, max_count=limit)


def get_template_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=template"
    return finder.all_templates(api_key, request_url, max_count=limit)


def get_instance_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=instance"
    return finder.all_templates(api_key, request_url, max_count=limit)


def get_template(api_key, server_address, template_id):
    request_url = server_address + "/templates/" + escape(template_id)
    return downloader.get_resource(api_key, request_url)


def get_element(api_key, server_address, element_id):
    request_url = server_address + "/template-elements/" + escape(element_id)
    return downloader.get_resource(api_key, request_url)


def get_instance(api_key, server_address, instance_id):
    request_url = server_address + "/template-instances/" + escape(instance_id)
    return downloader.get_resource(api_key, request_url)


def get_server_address(server):
    server_address = "http://localhost"
    if server == 'local':
        server_address = "https://resource.metadatacenter.orgx"
    elif server == 'staging':
        server_address = "https://resource.staging.metadatacenter.net"
    elif server == 'production':
        server_address = "https://resource.metadatacenter.net"

    return server_address


def create_empty_report():
    return defaultdict(list)


def escape(s):
    return quote(str(s), safe='')


def to_json_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True)
    else:
        return json.dumps(obj)


def consume(report, resource_id, status_code, server_message, **kwargs):
    if status_code > 200:
        error_message = str(status_code) + " " + server_message["status"]
        if detail_message(server_message):
            error_message += " - " + detail_message(server_message)[:80] + "..."  # get a snippet
        report[error_message].append(resource_id)
    else:
        is_valid = server_message["validates"]
        if is_valid == 'false':
            for error_details in server_message["errors"]:
                error_message = error_details['message'] + " at " + error_details['location']
                report[error_message].append(resource_id)
    print_progressbar(**kwargs)


def print_progressbar(**kwargs):
    if 'iteration' in kwargs and 'total_count' in kwargs:
        iteration = kwargs["iteration"]
        total_count = kwargs["total_count"]
        percent = 100 * (iteration / total_count)
        filled_length = int(percent)
        bar = "#" * filled_length + '-' * (100 - filled_length)
        print("\rProcessing (%d/%d): |%s| %d%% Complete" % (iteration, total_count, bar, percent), end='\r')


def detail_message(server_message):
    detail_message = None
    if "message" in server_message:
        detail_message = server_message["message"]
    elif "errorMessage" in server_message:
        detail_message = server_message["errorMessage"]
    return detail_message


def show(report):
    report_size = len(report)
    message = "No error was found."
    if report_size > 0:
        message = "Found " + str(report_size) + " validation error(s)."
        message += "\n"
        message += "Details: " + to_json_string(dict(report))
    print("\n" + message)
    print()


if __name__ == "__main__":
    main()