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

    def load_model_file(self, model_file, test=False):
        if test:
            real_path = '../test/' + model_file
        else:
            real_path = '../' + model_file

        self.prism_handler.loadModelFile(real_path)

    def check_bool_property(self, property_string):
        result = self.prism_handler.checkBoolProperty(property_string)
        return pythonify(result)

    def check_quant_property(self, property_string):
        result = self.prism_handler.checkQuantProperty(property_string)
        return pythonify(result)

    def synthesize_strategy(self, path, property_string):
        strat = self.prism_handler.synthesizeStrategy(property_string)
        # strat.exportToFile(path)
        # strat.getNextMove(0)
        # TODO: ugly, but works. fix later
        strategy = {}
        f = open('prismhandler/adv.tra', 'r')
        for line in f:
            split_line = line.split()
            if len(split_line) == 2:
                strategy[split_line[0]] = split_line[1]
        return strategy
