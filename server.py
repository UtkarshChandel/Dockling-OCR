import tempfile, os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB

app = FastAPI()

print("Loading Docling models.... (first time is slow)")
pipeline_options = PdfPipelineOptions()
pipeline_options.do_table_structure = True
pipeline_options.document_timeout = 90

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
print("Docling ready.")

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    file_content = await file.read()

    if len(file_content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    suffix = os.path.splitext(file.filename)[-1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        result = converter.convert(tmp_path)
        doc = result.document
        return JSONResponse({
            "markdown": doc.export_to_markdown(),
            "tables": [
                {
                    "index": i,
                    "markdown": tbl.export_to_dataframe().to_markdown() if hasattr(tbl, 'export_to_dataframe') else str(tbl),
                }
                for i, tbl in enumerate(doc.tables)
            ],
            "page_count": len(doc.pages)
        })
    finally:
        os.unlink(tmp_path)

@app.get("/health")
def health():
    return {"status": "ok"}