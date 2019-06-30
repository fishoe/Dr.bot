from modules.base import *

@event('test')
async def f1(bot,msg):
    await msg.channel.send('it is only for test')

@event('t2')
async def f2(bot,msg):
    await msg.channel.send('it is another func')
