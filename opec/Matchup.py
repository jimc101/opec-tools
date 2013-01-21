class Matchup(object):

    def __init__(self, cell_position, spacetime_position, reference_record):
        """
       Constructs a matchup object.

       @param cell_position a list containing the cell indices.

       @param spacetime_position a list containing the position in space and time.

       @param reference_record a record containing the reference positions in space and time.
        """

        self.__cell_position = cell_position
        self.__spacetime_position = spacetime_position
        self.__reference_record = reference_record
        self.__values = {}

    def get_cell_position(self):
        return self.__cell_position

    def get_spacetime_position(self):
        return self.__spacetime_position

    def get_reference_record(self):
        return self.__reference_record

    def add_variable_value(self, name, value):
        self.__values[name] = value

    def get_variable_values(self):
        return self.__values

    cell_position = property(get_cell_position)
    spacetime_position = property(get_spacetime_position)
    reference_record = property(get_reference_record)
    values = property(get_variable_values)

    def __str__(self):
        return ', '.join('%s: %s' % (k.replace('_Matchup__', ''), vars(self)[k]) for k in vars(self))

