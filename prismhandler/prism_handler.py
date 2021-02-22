from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError


# TODO: ugly stuff! makes a copy to separate from java gateway
def pythonify(gateway_obj):
    res_copy = []
    for res in gateway_obj:
        res_copy.append(res)
    return res_copy


class PrismHandler:

    def __init__(self):
        try:
            self.gateway = JavaGateway()
            self.prism_handler = self.gateway.entry_point.getPrismHandler()
            print('Successfully connected to PRISM java gateway!')
        except Py4JNetworkError as err:
            print('Py4JNetworkError:', err)
            print('It is most likely that you forgot to start the PRISM java gateway. '
                  'Compile and launch prismhandler/PrismEntryPoint.java!')