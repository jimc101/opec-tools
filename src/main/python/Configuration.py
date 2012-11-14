PROPERTY_INPUT_FILE = "com.bc.opec.inputFile"

class Configuration:

    def __init__(self, dictionary):
        self.inputFile = dictionary[PROPERTY_INPUT_FILE]
