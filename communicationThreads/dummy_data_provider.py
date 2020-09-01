import random


class DummyDataProvider:
    @staticmethod
    def provide_dummy_data(len=None, spec = None):
        data = []
        if spec ==None:
            for i in range(len):
                data.append(random.randint(0,100))
        elif spec!='all':
            data.append(spec)
            for i in range(3):
                data.append(random.randint(0,10))
        elif spec=='all':
            data.append(spec)
            for i in range(9):
                data.append(random.randint(0,10))
        return data
