from onemodel.objects.object import Object
from onemodel.scope import Scope
from onemodel.namespace import Namespace


class Function(Object):
    """A code that will be executed in a separate namespace. 

    Parameters
    ----------
    argument_names : :obj:`list` of :obj:`str`
        Names of the arguments.
    body : :obj:`function`
        A Python function object.
    """

    def __init__(self):
        super().__init__()

        self["argument_names"] = []
        self["body"] = None

    def call(self, scope, argument_values):
        """Execute the function body. 

        Parameters
        ----------
        scope : :obj:`Scope`
            The scope where the function is called.
        parameter_names : :obj:`list` of :obj:`str`
            The values of the arguments passed to the function.
        """

        func_namespace = self.create_function_namespace(
            scope, 
            argument_values
        )

        scope.push(func_namespace)
        result = self["body"](scope)
        scope.pop()

        return result

    def create_function_namespace(self, scope, argument_values):
        """Create the local namespace for the execution of the function.

        Parameters
        ----------
        scope : :obj:`Scope`
            The scope where the function is called.
        parameter_names : :obj:`list` of :obj:`str`
            The values of the arguments passed to the function.
        """

        result = Namespace()

        if argument_values is None:
            return result

        for name, value in zip(self["argument_names"], argument_values):
            result[name] = value

        return result
