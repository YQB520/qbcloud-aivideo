from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 检查 Authorization
        auth_token = request.headers.get("Authorization")

        if not auth_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # 如果验证通过，继续处理请求
        response = await call_next(request)
        return response
