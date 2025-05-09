#from aiogram import BaseMiddleware
##from aiogram.types import TelegramObject
#from core.t_cc import TelegramClientContext
#from typing import (
#    Callable, 
#    Awaitable, 
#    Dict, 
#    Any
#)

#class ClientContextMiddleware(BaseMiddleware):
#    async def __call__(
#        self,
#        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#        event: TelegramObject,
#        data: Dict[str, Any],
#    ) -> Any:

#        from_user = data.get("event_from_user") or getattr(event, "from_user", None)

#        if from_user:
#           client_context = TelegramClientContext(from_user)
#            data["client_context"] = client_context
#        return await handler(event, data)