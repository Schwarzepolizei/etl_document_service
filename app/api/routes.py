from fastapi import APIRouter, UploadFile, File
from app.pipeline.etl_pipeline import run_etl
from app.schemas.document import ETLResponse

router = APIRouter()


@router.post("/process", response_model=ETLResponse)
async def process_file(file: UploadFile = File(...)):
    result = run_etl(file.filename)
    return result