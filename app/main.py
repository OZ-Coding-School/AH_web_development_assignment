from fastapi import FastAPI
import uvicorn
from starlette.staticfiles import StaticFiles

app = FastAPI()

# 'static' 폴더를 '/static' 경로로 마운트 (CSS, JS 파일 서빙용)
app.mount("/static", StaticFiles(directory="static"), name="static")
# 'media' 폴더를 '/media' 경로로 마운트 (사용자 업로드 파일 서빙용)
app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=8001, app="main:app", reload=True)
