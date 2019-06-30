class Loader:
    _instance = None
    def __init__(self):
        self.eventList = {}
        self.eventProc = None
        return

    @classmethod
    def hasKwd(cls,kwd):
        if cls._instance is None:
            cls._instance = Loader()
        if kwd in cls._instance.eventList:
            return True
        else :
            return False

    @classmethod
    def addEvent(cls,kwd,event):
        if cls._instance is None:
            cls._instance = Loader()
        cls._instance.eventList[kwd] = event

    @classmethod
    def setProc(cls,proc):
        if cls._instance is None:
            cls._instance = Loader()
        cls._instance.eventProc = proc

    @classmethod
    def load(cls):
        m = Module()
        if cls._instance.eventProc is None :
            m.setEvents(cls._instance.eventList)
            cls._instance.eventList.clear()
        else :
            m.setProc(cls._instance.eventProc)
            cls._instance.eventProc = None
        cls._instance = None
        return m

class Module:
    """
    msg_proc has a procedure from Module Object
    """
    def __init__(self):
        self.name = str()
        self.pref = str()
        self.mInst = None
        self.proc = None
        self.events = {}
        pass

    def __del__(self):
        del self.name
        del self.pref
        del self.mInst
        del self.proc
        self.events.clear()
        del self.events
        pass

    async def msgProc(self,bot,msg):
        result = False # result of this module
        if self.proc is None :
            line = str.lstrip(msg.content[len(bot.getPref()):])
            if self.pref == '' :
                param = cmdParse(line)
                if param['cmd'] in self.events:
                    await self.events[param['cmd']](bot,msg)
                    return True
                else :
                    return False
            elif line.startswith(self.pref) :
                line = str.lstrip(line[len(m_pref):])
                param = cmdParse(line)
                if param['cmd'] in self.events:
                    await self.events[param['cmd']](bot,msg)
                    return True #end point of procedure
                else : return False #escape
        else :
            result = await self.proc(bot,msg)
        return result

    def setModule(self,name,modInst):
        self.name = name
        self.mInst = modInst

    def setProc(self, proc):
        assert self.events is {}
        self.proc = proc

    def setEvents(self, eList):
        assert self.proc is None
        self.events = eList.copy()

    def __eq__(self, value):
        if type(value) is str:
            if self.name == value :
                return True
            else :
                return False
        elif type(value) is Module:
            if self.name == value.name :
                return True
            else :
                return False
        else :
            return False #raise Exception

def mod_proc():
    """
    decorator
    register a function as event_procedure
    """
    def inner(func):
        Loader.setProc(func)
    return inner

def event(kwd):
    """
    decorator
    register a function with kwd on list
    """
    def inner(func):
        assert str.count(kwd,' ') is 0
        if Loader.hasKwd(kwd) :
            raise Exception("duplicate of events in the same module")
        else :
            Loader.addEvent(kwd,func)
    return inner

def cmdParse(line):
    gen = (wd for wd in line.split())
    kwd = next(gen)
    result = {'cmd':kwd}
    try :
        while True :
            kwd = next(gen)
            if kwd.startswith('-') is not True :
                if 'args' in result:
                    result['args'] = result['args'] +' '+ kwd
                else :
                    result['args'] = kwd
            else :
                break
        while True :
            if kwd.startswith('-') :
                opt = kwd
                if opt in result:
                    kwd = next(gen)
                    continue
                result[opt]=None
            else :
                if result[opt] is None :
                    result[opt]=kwd
                else :
                    result[opt]= result[opt] +' '+kwd
            kwd = next(gen)
    except StopIteration :
        return result