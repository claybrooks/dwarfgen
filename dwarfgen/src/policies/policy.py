class Policy:
    def __init__(self):
        pass

    def check(self, die, **kwargs):
        raise NotImplementedError("Base class 'Policy' needs to be implemented")
