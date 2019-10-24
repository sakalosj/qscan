class CustomNS:
    @classmethod
    def keys(cls):
        return [i for i in cls.__dict__.keys() if i[:1] != '_']

    @classmethod
    def values(cls):
        return [i[1] for i in cls.__dict__.items() if i[0][:1] != '_']

