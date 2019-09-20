import sys
import os
import torch


class Setup(object):
    def setup(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()


class FileSetup(object):
    path = None

    def shutdown(self):
        if os.path.exists(self.path):
            # os.remove(self.path)
            pass


class EvalModeForLoadedModule(FileSetup):
    path = 'dropout_model.pt'

    def setup(self):
        class Model(torch.jit.ScriptModule):
            def __init__(self):
                super(Model, self).__init__()
                self.dropout = torch.nn.Dropout(0.1)

            @torch.jit.script_method
            def forward(self, x):
                x = self.dropout(x)
                return x

        model = Model()
        model = model.train()
        model.save(self.path)


class SerializationInterop(FileSetup):
    def __init__(self, device):
        self.device = device
        self.path = 'ivalue_{}.pt'.format(device)

    def setup(self):
        ones = torch.ones(2, 2, device=self.device)
        twos = torch.ones(3, 5, device=self.device) * 2

        value = (ones, twos)

        torch.save(value, self.path)


tests = [
    EvalModeForLoadedModule(),
    SerializationInterop('cpu'),
    SerializationInterop('cuda'),
]

def setup():
    for test in tests:
        test.setup()


def shutdown():
    for test in tests:
        test.shutdown()


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "setup":
        setup()
    elif command == "shutdown":
        shutdown()
