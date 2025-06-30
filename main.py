# relay_server.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

# CORS 설정 (모든 origin 허용 또는 필요한 도메인만 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 내부 상태 저장 =====
recipe_storage: List[str] = []
manufacture_complete: bool = False
current_recipe_id: Optional[str] = None

# ===== 데이터 모델 =====
class RecipeRequest(BaseModel):
    recipe_id: str
    ingredients: List[str]

class StatusResponse(BaseModel):
    success: bool
    done: Optional[bool] = None
    ingredients: Optional[List[str]] = None
    message: Optional[str] = None

# ===== API 엔드포인트 =====

@app.post("/send_recipe", response_model=StatusResponse)
async def send_recipe(recipe: RecipeRequest):
    global recipe_storage, manufacture_complete, current_recipe_id
    recipe_storage = recipe.ingredients
    current_recipe_id = f"{recipe.recipe_id}_{str(uuid4())[:8]}"  # 예: abc123_9a3f5c2e
    manufacture_complete = False
    return StatusResponse(success=True, message="레시피 저장 완료")


@app.get("/get_recipe", response_model=StatusResponse)
async def get_recipe():
    if recipe_storage and current_recipe_id:
        return StatusResponse(
            success=True,
            ingredients=recipe_storage,
            message=current_recipe_id
        )
    return StatusResponse(success=False, message="레시피 없음")

@app.get("/get_recipe_id")
async def get_recipe_id():
    return {"recipe_id": current_recipe_id}


@app.post("/mark_done", response_model=StatusResponse)
async def mark_done():
    global manufacture_complete
    manufacture_complete = True
    return StatusResponse(success=True, message="제조 완료로 표시됨")


@app.get("/check_status", response_model=StatusResponse)
async def check_status():
    return StatusResponse(success=True, done=manufacture_complete)

@app.get("/current_ingredients")
async def current_ingredients():
    return await get_recipe()

@app.get("/status", response_model=StatusResponse)
async def status_alias():
    return await check_status()

@app.post("/done")
async def done():
    return await mark_done()
