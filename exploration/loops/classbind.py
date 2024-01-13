class WhileIter:
    # stop = StopIteration

    def __next__(self):
        if False: raise StopIteration
        return self.scope