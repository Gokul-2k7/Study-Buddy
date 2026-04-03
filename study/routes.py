import uuid
import chromadb
from flask import Flask, render_template, request, redirect, url_for, Blueprint
from main import db,bcrypt
from models import Document
from forms import UploadForm
from flask_login import login_required, current_user
import pdfplumber 
study=Blueprint('study', __name__, url_prefix='/study')


def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        pages=[]
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)

def chunk_text(text, max_size=800, overlap=100):
    pages=[para for para in text.split("\n\n") if para.strip()]
    chunks=[]
    current=""
    for page in pages:
        if len(page) > max_size:
            for i in range(0, len(page), max_size - overlap):
                chunk=page[i:i+max_size]
                chunks.append(chunk.strip())
                continue
        else:
            if(len(current)+len(page)+1) <= max_size:
                current+=page
            else:
                chunks.append(current.strip())
                overlap_text=" ".join(current.split()[-20:])
                current=overlap_text+" "+page

    if current:
        chunks.append(current.strip())
    return chunks

@study.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form=UploadForm()
    if form.validate_on_submit():
        file=form.documnent.data
        temp=f"tmp/{uuid.uuid4()}.pdf" # Generate a unique filename
        file.save(temp)
        text=extract_text_from_pdf(temp)
        chunks=chunk_text(text)
        client=chromadb.Client()
        collection_name = f"user_{current_user.id}_doc_{uuid.uuid4().hex[:8]}"
        collection = client.get_or_create_collection(collection_name)
        collection.add(
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"doc_id": collection_name, "chunk_index": i} for i in range(len(chunks))], 
        )
    
    return render_template('upload.html', form=form)

