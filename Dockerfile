FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install docling fastapi uvicorn python-multipart

# Pre-download all models so the pod starts fast
RUN python3 <<'EOF'
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
opts = PdfPipelineOptions()
opts.do_table_structure = True
opts.document_timeout = 90
DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
print('Models cached.')
EOF

COPY server.py .

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]