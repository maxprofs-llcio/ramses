from __future__ import print_function
import inflection


class ContentTypes(object):
    """ ContentType values.

    """
    JSON = 'application/json'
    TEXT_XML = 'text/xml'
    MULTIPART_FORMDATA = 'multipart/form-data'
    FORM_URLENCODED = 'application/x-www-form-urlencoded'


def fields_dict(raml_schema, schema_ct):
    """ Restructure `raml_schema` to a dictionary that looks like
    {field_name: {required: boolean, type: type_name}, ...}

    Operations performer depend on a Content Type of `schema` which
    is passed as `schema_ct` argument.

    Arguments:
        :raml_schema: pyraml.entities.RamlBody.schema.
        :schema_ct: ContentType of the schema as a string from RAML file.
    """
    if schema_ct == ContentTypes.JSON:
        return raml_schema['properties']
    if schema_ct == ContentTypes.TEXT_XML:
        # Process XML schema
        pass


def is_dynamic_uri(uri):
    """ Determine whether `uri` is a dynamic uri or not.

    Assumes dynamic uri is a uri that ends with '}' which is a Pyramid
    way to define dynamic parts in uri.

    Arguments:
        :uri: URI as a string.
    """
    return uri.endswith('}')


def clean_dynamic_uri(uri):
    """ Strips /, {, } from dynamic `uri`.

    Arguments:
        :uri: URI as a string.
    """
    return uri.replace('/', '').replace('{', '').replace('}', '')


def resource_model_name(parent_resource, route_name):
    """ Generate model name.

    Model name is generated using `parent_resource`s `uid` which contains
    all resources chain in a form if 'parent:child' and a name of the route
    `route_name`.

    Arguments:
        :parent_resource: Instance of `nefertari.resource.Resource`.
        :route_name: String representing route's name.
    """
    if parent_resource.uid:
        uid = parent_resource.uid + ':' + route_name
    else:
        uid = route_name
    uid = inflection.camelize(uid.replace(':', '_'))
    return inflection.singularize(uid)


def resource_view_attrs(raml_resource):
    """ Generate view methods names needed for `raml_resource` view.

    Collects HTTP method names from `raml_resource.methods` and
    dynamic child `methods` if child exists. Collected methods are
    then translated  to `nefertari.view.BaseView` methods' names
    each of which if used to process a particular HTTP method request.

    Maps of {HTTP_method: view_method} `collection_methods` and
    `item_methods` are used to convert collection and item methods
    respectively.

    Arguments:
        :raml_resource: Instance of pyraml.entities.RamlResource.
    """
    from .views import collection_methods, item_methods

    http_methods = (raml_resource.methods or {}).keys()
    attrs = [collection_methods.get(m.lower()) for m in http_methods]

    # Check if resource has dynamic subresource like collection/{id}
    subresources = raml_resource.resources or {}
    dynamic_res = [res for uri, res in subresources.items()
                   if is_dynamic_uri(uri)]

    # If dynamic subresource exists, add its methods to attrs, as both
    # resources are handled by a single view
    if dynamic_res and dynamic_res[0].methods:
        http_submethods = (dynamic_res[0].methods or {}).keys()
        attrs += [item_methods.get(m.lower()) for m in http_submethods]

    return set(filter(bool, attrs))
