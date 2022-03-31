from tartiflette import Resolver

@Resolver("Query.ping")
async def ping(parent, args, ctx, info):
    return "pong"
