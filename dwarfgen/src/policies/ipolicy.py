class IPolicy:
    def __init__(self):
        pass

    def __call__(self, die, **kwargs):
        return self.check(die, **kwargs)

    def check(self, die, **kwargs):
        raise NotImplementedError("Base class 'Policy' needs to be implemented")
