from fastapi import APIRouter, UploadFile, File
from app.pipeline.etl_pipeline import run_etl

router = APIRouter()


@router.post("/process")
async def process_file(file: UploadFile = File(...)):
    result = run_etl(file.filename)
    return result