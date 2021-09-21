from onemodel.dsl.values.value import Value

class PythonValue(Value):
    """ PythonValue holds the value of a regular python object.
    """
    def __init__(self, value):
        """ Initialize PythonValue
        """
        super().__init__()
        self.value = value
    
    def add_value_to_model(self, name, model):
        # PythonValues are not included in SBML models.
        pass

    def __str__(self):
        return str(self.value)
        
    def __repr__(self):
        return repr(self.value)