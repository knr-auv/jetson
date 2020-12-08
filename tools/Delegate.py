class Delegate(object):
    """Class that holds reference to methods, so they can be called collectively.
       It is ment to use for implementing events and call-backs.
    """
    __callbackList = list()
    def __call__(self, *args,**kwargs):
        self.Invoke(*args, **kwargs)
    def __init__(self):
        self.__callbackList = list()

    def __iadd__(self, other):
        self.Register(other)
        return self

    def __isub__(self, other):
        self.Remove(other)
        return self
    
    def Register(self, fun):
        for i in self.__callbackList:
            if i == fun:
                return
        self.__callbackList.append(fun)
        
    def Remove(self, fun):
        lenght = len(self.__callbackList)
        for i in range(lenght):
            if self.__callbackList[i]==fun:
                self.__callbackList.pop(i)
                return

    def Invoke(self, *args,**kwargs):
        args_lenght= len(args)
        kwargs_lenght = len(kwargs)
        for i in self.__callbackList:
            if args_lenght==0 and kwargs_lenght == 0:
                i()
            else:
                i(*args,**kwargs)
            
