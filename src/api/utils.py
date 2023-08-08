from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def create_response(answer, status_code: int = 200) -> JSONResponse:
    if status_code < 400:
        data = answer
    else:
        data = {
            "success": False,
            "errors": [{"message": answer}]
        }
    return JSONResponse(content=jsonable_encoder(data), status_code=status_code)
