from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.utils import save_uploaded_document

router = APIRouter(
    prefix="/documents",
    tags=["Documentos"]
)

@router.post("/upload/")
async def upload_document(
    
    file: UploadFile = File(...)):
    """
    Sube un archivo PDF, Word o Excel al servidor y devuelve su ruta de almacenamiento.
    """
    try:
        file_path = save_uploaded_document(file)
        return {
            "message": "Archivo subido correctamente",
            "filename": file.filename,
            "ruta_servidor": file_path
        }
    except HTTPException as e:
        # Retorna los errores personalizados definidos en la función
        raise e
    except Exception as e:
        # Captura cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
