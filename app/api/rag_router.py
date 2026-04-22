import json

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.pipeline.etl_pipeline import run_etl
from app.rag.index_builder import IndexBuilder
from app.rag.index_store import FaissIndexStore
from app.rag.retriever import Retriever
from app.schemas.rag import SearchRequest, SearchResponse, IndexResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=IndexResponse)
async def index_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        etl_response = run_etl(file.filename, file_bytes)
        etl_dict = etl_response.model_dump()

        if etl_dict["processing"]["status"] != "success":
            raise HTTPException(status_code=400, detail=etl_dict["processing"]["errors"])

        builder = IndexBuilder()
        result = builder.build_from_etl_response(etl_dict)
        return IndexResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        retriever = Retriever()
        results = retriever.search(request.query, request.top_k)

        return SearchResponse(
            query=request.query,
            top_k=request.top_k,
            results=results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/index")
async def clear_index():
    try:
        store = FaissIndexStore()
        store.clear()
        return {"status": "success", "message": "Index cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))