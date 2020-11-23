class Delegate(object):
    __callbackList = list()

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
        l = len(self.__callbackList)
        for i in range(l):
            if(self.__callbackList[i]==fun):
                self.__callbackList.pop(i)
                return

    def Invoke(self, *args,**kwargs):
        l= len(args)
        k = len(kwargs)
        for i in self.__callbackList:
            
            if l==0 and k == 0:
                i()
            else:
                i(*args,**kwargs)
            
