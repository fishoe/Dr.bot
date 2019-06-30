import discord
from importlib import import_module, reload
import os

class BotCore(discord.Client):
    def __init__(self):
        self._bltinCmds = {}
        self._builtin()
        self.pref = str() #init pref as null
        ModMgr.getInst()
        assert ModMgr is not None
        return super().__init__()

    async def on_ready(self):
        """
        before getting into main procedure
        implements this codes
        """
        assert ModMgr.getInst() is not None

    async def on_message(self, msg):
        """
        """
        if self.user == msg.author :
            return

        mention = self._getMention(msg)

        #when bot mentioned
        if msg.content.startswith(mention):
            cmd = str.lstrip(msg.content[len(mention):]).split()[0]
            if cmd in self._bltinCmds :
                await self._bltinCmds[cmd](bot,msg)
            return

        #district channels

        #call mods
        await ModMgr.msgProc(self,msg)

    def _addbltinCmds(self,kwd, func) :
        if kwd in self._bltinCmds :
            assert False
        self._bltinCmds[kwd] = func
        
    def _getMention(self,msg) :
        """
        return mentioned str of this bot
        """
        mention = str()
        if msg.guild.get_member(self.user.id).nick is None :
            mention = "<@{}>".format(self.user.id)
        else :
            mention = "<@!{}>".format(self.user.id)
        return mention

    def _builtin(self):
        async def bltinList(bot,msg):
            """
            short comments for this function
            """
            if self._bltinCmds is {}:
                msg.channel.send("no commands") #need to fix
            else :
                e = discord.Embed(title = "built-in commands List")
                for kwd in self._bltinCmds.keys() :
                    e.add_field(name = kwd, value = None)
                await msg.channel.send(embed = e)
        self._addbltinCmds('cmds',bltinList)

        async def loadMod(bot, msg):
            mention = self._getMention(msg)
            #line = msg.content[len(mention):].split()
            #cmd = line[0]
            #args = line[1:]
            args = msg.content[len(mention):].split()[1:]

            for i in args :
                if i in ModMgr.getModList() :
                    await msg.channel.send("already loaded module {}".format(i))
                    return
                if ModMgr.loadMod(i):
                    await msg.channel.send("succeed to load {}".format(i))
                else :
                    await msg.channel.send("failed to load {}".format(i))
            pass
        self._addbltinCmds('load',loadMod)

        async def unloadMod(bot,msg):
            mention = self._getMention(msg)
            args = msg.content[len(mention):].split()[1:]

            #if msg had modname check if modlist has this name
            for i in args :
                if ModMgr.unloadMod(i) :
                    await msg.channel.send("unloaded Module:{}".format(i))
                else :
                    await msg.channel.send('i could not find module:{}'.format(i))
        self._addbltinCmds('unload',unloadMod)

        async def echoMsg(bot,msg) :
            mention = self._getMention(msg)
            line = msg.content[len(mention):]
            await msg.channel.send(line)
        self._addbltinCmds('echo',echoMsg)

        async def loadedMods(bot, msg) :
            modList = ModMgr.getModList()
            if len(modList) > 0 :
                e = discord.Embed(title = "loaded module list")
                for mod in modList :
                    e.add_field(name = mod.name, value = None)
                await msg.channel.send(embed = e)
        self._addbltinCmds('loaded',loadedMods)

        async def loadableFiles(bot, msg) :
            files = os.listdir( ModMgr.getPath())
            files.remove('base.py')
            e = discord.Embed(title = 'module files list')
            for f in files :
                if ('__' in f) is False :
                    e.add_field(name = f, value = None)
            await msg.channel.send(embed = e)
        self._addbltinCmds('loadable',loadableFiles)

        pass #end enrole built-in functions

    def getPref(self):
        return self.pref

class ModMgr:
    _instance = None
    mDir ='modules'

    def __init__(self):
        self.mods = []
        self.loaded = []

    @classmethod
    def getInst(cls):
        if cls._instance is None :
            cls._instance = ModMgr()
        return cls._instance

    @classmethod
    def loadMod(cls,modName):
        files = os.listdir( os.path.join(os.getcwd(),ModMgr.mDir))
        files.remove('base.py')
        #if file exist, check this file has syntax error
        if '{}.py'.format(modName) in files :
            if not modName in ModMgr.getModList() :
                try :
                    mInst = import_module('.{}'.format(modName),ModMgr.mDir)
                    if ModMgr._isloaded(modName):
                        mInst = reload(mInst)
                    m = mInst.Loader.load()
                    m.setModule(modName, mInst)
                    ModMgr._addMod(m)
                    return True
                except SyntaxError as e:
                    print("syntax")
                    print(e)
                    return False
                except :
                    print("unknown")
                    return False
            else : 
                print('already loaded module name')
                return False
        else :
            print('no file')
            return False

    @classmethod
    def unloadMod(cls,modName):
        for mod in cls.getModList() :
            try :
                if mod == modName :
                    ModMgr.getModList().remove(mod)
                    del mod
                    return True
            except ValueError as e:
                print('no value in list')
                print(e)
                return False
            except :
                print('unknown')
        print('have not loaded yet')
        return False

    @classmethod
    def getModList(cls):
        return cls._instance.mods

    @classmethod
    def getPath(cls):
        return os.path.join(os.getcwd(),ModMgr.mDir)

    @classmethod
    def _addMod(cls,module) : 
        assert module is not None
        cls._instance.mods.append(module)
        cls._instance.loaded.append(module.name)

    @classmethod
    def _isloaded(cls,modName) :
        if modName in cls._instance.loaded :
            return True
        else :
            return False

    @classmethod
    async def msgProc(cls,bot,msg):
        for mod in cls._instance.mods :
            result = await mod.msgProc(bot,msg)
            if result is True :
                return mod
        return False

bot = BotCore()
bot.run('NTk0ODE5OTk0OTM2OTM0NDEw.XRh_Zw.MLECvzXQL9M8QsiyGpDqTEmXxI4')