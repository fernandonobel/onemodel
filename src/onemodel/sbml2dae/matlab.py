from tokenize import tokenize, NAME, OP, ENCODING
from io import BytesIO

from onemodel.sbml2dae.dae_model import DaeModel, StateType

class Matlab:
    """ Takes a DAE model as input and exports a matlab implementation.
    """
    def __init__(self, dae, output_path):
        """ Inits Matlab.
        """
        self.dae = dae
        self.output_path = output_path

    def string2matlab(self, math_expr):
        """ Parses a libSBML math string formula into a matlab expression.

        Arguments:
            math_expr: str
                Math formula obtained with libSBML.formulaToL3String()
        """
        result = ''

        parameters = []
        for item in self.dae.getParameters():
            parameters.append(item['id'])

        g = tokenize(BytesIO(math_expr.encode('utf-8')).readline)

        for toknum, tokval, _, _, _ in g:
            if toknum == ENCODING:
                continue

            elif toknum == NAME and tokval in parameters:
                result += 'p.' + str(tokval)

            elif toknum == OP and tokval in ('*','/','^'):
                result += '.' + str(tokval)

            elif toknum == OP and tokval in ('+','-'):
                result += ' ' + str(tokval) + ' '

            else:
                result += str(tokval)

        return result

    def getStates(self, math_expr):
        """ Return a list with the states present in the string.
        """
        result = []

        states = []
        for state in self.dae.getStates():
            states.append(state['id'])

        g = tokenize(BytesIO(math_expr.encode('utf-8')).readline)

        for toknum, tokval, _, _, _ in g:
            if toknum == NAME and tokval in states:
                result.append(tokval)

        return result

    def writeWarning(self, f):
        f.write(f'% This file was automatically generated by onemodel.\n')
        f.write(
            f'% Any changes you make to it will be overwritten the next time\n'
        )
        f.write(f'% the file is generated.\n\n')

    def writeStates(self, f):
        # List of states that are already defined in the file.
        known_states = []
        states_num = len(self.dae.getStates())

        # Write ODE and ALGEBRAIC states.
        f.write(f'% ODE and algebraic states:\n')
        i = 1
        for state in self.dae.getStates():
            # Skip not ODE or ALGEBRAIC states.
            if not state['type'] in (StateType.ODE, StateType.ALGEBRAIC):
                continue

            f.write(f'{state["id"]} = x({i},:);\n')
            known_states.append(state['id'])
            i += 1
        f.write(f'\n')

        f.write(f'% Assigment states:\n')

        while len(known_states) != states_num:
            for state in self.dae.getStates():
                # Skip not ASSIGMENT states.
                if not state['type'] == StateType.ASSIGMENT:
                    continue

                # Skipe states that are already defined.
                if state in known_states:
                    continue

                dependencies = self.getStates(state['equation'])

                if all(elem in known_states for elem in dependencies):
                    equation = self.string2matlab(state['equation'])
                    f.write(f'{state["id"]} = {equation};\n')
                    known_states.append(state['id'])

        f.write(f'\n')

    def exportDefaultParameters(self):
        """ Generate Matlab function which returns the default parameters.
        """
        filepath = self.output_path
        filepath += '/'
        filepath += self.dae.getModelName()
        filepath += '_param.m'

        # Create and open the file to export.
        f = open(filepath, "w")

        # Function header.
        f.write(f'function [p,x0,M] = {self.dae.getModelName()}_param()\n')
        self.writeWarning(f)

        # Default parameters.
        f.write(f'% Default parameters value.\n')
        for item in self.dae.getParameters():
            f.write(f'p.{item["id"]} = {item["value"]};\n')

        ## Default initial conditions.
        f.write(f'\n% Default initial conditions.\n')
        f.write(f'x0 = [\n')
        for item in self.dae.getStates():
            if item['type'] == StateType.ODE:
                f.write(
                    f'\t{item["initialCondition"]} % {item["id"]}\n'
                )
            elif item['type'] == StateType.ALGEBRAIC:
                f.write(
                    f'\t{item["initialCondition"]} % {item["id"]} (algebraic)\n'
                )
        f.write(f'];\n')

        # Mass matrix.
        f.write(f'\n% Mass matrix for algebraic simulations.\n')
        f.write(f'M = [\n')
        M = []
        for item in self.dae.getStates():
            if item['type'] == StateType.ODE:
                M.append(1)
            elif item['type'] == StateType.ALGEBRAIC:
                M.append(0)

        i = 0
        i_max = len(M)
        while i < i_max:
            f.write('\t')
            f.write('0 '*i)
            f.write(f'{M[i]} ')
            f.write('0 '*(i_max-i-1))
            f.write('\n')
            i += 1

        f.write(f'];\n')

        f.write(f'\nend\n')

        f.close()

        return filepath

    def exportOde(self):
        """ Generate Matlab function which evaluates the Ode.
        """
        filepath = self.output_path
        filepath += '/'
        filepath += self.dae.getModelName()
        filepath += '_ode.m'

        # Create and open the file to export.
        f = open(filepath, "w")

        # Function header.
        f.write(f'function [dx] = {self.dae.getModelName()}_ode(t,x,p)\n')
        self.writeWarning(f)

        # Comment arguments.
        f.write(f'\n% Args:\n')
        f.write(f'%\t t Current time in the simulation.\n')
        f.write(f'%\t x Array with the state value.\n')
        f.write(f'%\t p Struct with the parameters.\n')

        # Comment return.
        f.write(f'\n% Return:\n')
        f.write(f'%\t dx Array with the ODE.\n')
        f.write(f'\n')

        self.writeStates(f)
       
        # Generate ODE equations.
        i = 1
        for item in self.dae.getStates():
            string = f'% der({item["id"]})\n'

            if item['type'] == StateType.ODE:
                equation = self.string2matlab(item['equation'])
                string += f'dx({i},1) = {equation};\n\n'
                f.write(string)
                i += 1

            elif item['type'] == StateType.ALGEBRAIC:
                equation = self.string2matlab(item['equation'])
                string += f'dx({i},1) = {equation};\n\n'
                f.write(string)
                i += 1

        f.write(f'end\n')
        f.close()

        return filepath

    def exportStates(self):
        """ Generate Matlab function which calculates all model states.
        """
        filepath = self.output_path
        filepath += '/'
        filepath += self.dae.getModelName()
        filepath += '_states.m'

        # Create and open the file to export.
        f = open(filepath, "w")

        # Function header.
        f.write(f'function [out] = {self.dae.getModelName()}_states(t,x,p)\n')
        self.writeWarning(f)

        self.writeStates(f)

        # Save the time.
        f.write(f'% Save simulation time.\n')
        f.write(f'out.t = t;')
        f.write(f'\n')

        # Crate ones vector.
        f.write(f'\n')
        f.write('% Vector for extending single-value states and parameters.\n')
        f.write('ones_t = ones(size(t));\n')
        f.write(f'\n')

        # Save states.
        f.write(f'\n% Save states.\n')
        for item in self.dae.getStates():
                f.write(f'out.{item["id"]} = {item["id"]}.*ones_t;\n')
        f.write(f'\n')

        # Save parameters.
        f.write(f'% Save parameters.\n')
        for item in self.dae.getParameters():
            f.write(f'out.{item["id"]} = p.{item["id"]}.*ones_t;\n')
        f.write(f'\n')

        f.write(f'end\n')

        f.close()

        return filepath

    def exportDriver(self):
        """ Generate an example driver script.
        """
        filepath = self.output_path
        filepath += '/'
        filepath += self.dae.getModelName()
        filepath += '_driver.m'

        # Create and open the file to export.
        f = open(filepath, "w")

        # Function header.
        name = self.dae.getModelName() 
        f.write(f'%% Example driver script for simulating "{name}" model.\n')
        self.writeWarning(f)

        # Clear and close all.
        f.write(f'clear all;\n')
        f.write(f'close all;\n')

        # Default parameters.
        f.write(f'\n% Default parameters.\n')
        f.write(f'[p,x0,M] = {name}_param();\n')

        # Solver options.
        f.write(f'\n% Solver options.\n')
        f.write(f"opt = odeset('AbsTol',1e-8,'RelTol',1e-8);\n")
        f.write(f"opt = odeset(opt,'Mass',M);\n")

        # Simulation time span.
        f.write(f'\n% Simulation time span.\n')
        f.write(f'tspan = [0 50];\n')

        # Simulate.
        f.write(f'\n[t,x] = ode15s(@(t,x) {name}_ode(t,x,p),tspan,x0,opt);\n')
        f.write(f'out = {name}_states(t,x,p);\n')
        
        # Plot.
        f.write(f'\n% Plot result.\n')
        f.write(f'plot(t,x);\n')
        f.write(f'grid on;\n')
        # TODO: Add a legend.


        f.close()

        return filepath
       

if __name__ == '__main__':
    dae = DaeModel(
        '/home/nobel/Sync/python/workspace/onemodel/examples/build/basic.xml'
    )

    matlab = Matlab(
        dae,
        '/home/nobel/Sync/python/workspace/onemodel/examples/build'
    )

    matlab.exportDefaultParameters()
    matlab.exportOde()
    matlab.exportStates()
    matlab.exportDriver()
