from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError


# TODO: ugly stuff! makes a copy of the array to separate result from Py4J (java gateway)
def pythonify(gateway_obj):
    res_copy = []
    for res in gateway_obj:
        res_copy.append(res)
    return res_copy


class PrismHandler:

    def __init__(self):
        self.gateway = JavaGateway()
        self.prism_handler = self.gateway.entry_point.getPrismHandler()

    def load_model_file(self, model_file):
        self.prism_handler.loadModelFile(model_file)

    def check_bool_property(self, property_string):
        result = self.prism_handler.checkBoolProperty(property_string)
        return pythonify(result)
