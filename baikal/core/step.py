from typing import List, Union, Tuple

from baikal.core.data import Data, is_data_list
from baikal.core.digraph import Node
from baikal.core.utils import listify


class Step(Node):
    def __init__(self, *args, name=None, **kwargs):
        super(Step, self).__init__(*args, name=name, **kwargs)
        self.inputs = None
        self.outputs = None

    def __call__(self, inputs):
        inputs = listify(inputs)

        if not is_data_list(inputs):
            raise ValueError('Steps must be called with Data inputs.')

        # Add edges
        for input in inputs:
            predecessor = input.node
            self.graph.add_edge(predecessor, self)

        self.inputs = inputs
        self.outputs = self._build_outputs(inputs)

        return self.outputs

    # TODO: We might need a check_inputs method as well (Concatenate, Split, Merge, etc will need it).
    # Also, sklearn-based Steps can accept only shapes of length 1
    # (ignoring the samples, the dimensionality of the feature vector)

    def _build_outputs(self, inputs: List[Data]) -> Union[Data, List[Data]]:
        input_shapes = [input.shape for input in inputs]
        output_shapes = self.build_output_shapes(input_shapes)

        if len(output_shapes) == 1:
            return Data(output_shapes[0], self, 0)

        return [Data(shape, self, i) for i, shape in enumerate(output_shapes)]

    def build_output_shapes(self, input_shapes: List[Tuple]) -> List[Tuple]:
        raise NotImplementedError

    def compute(self, *inputs):
        raise NotImplementedError


class InputNode(Node):
    def __init__(self, shape, name=None):
        super(InputNode, self).__init__(name=name)
        # TODO: Maybe '/0' at the end is cumbersome and unnecessary in InputNode's
        self.outputs = Data(shape, self)


def Input(shape, name=None):
    # Maybe this can be implemented in InputNode.__new__
    input = InputNode(shape, name)
    return input.outputs