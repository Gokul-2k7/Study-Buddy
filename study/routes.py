import os
import uuid
import chromadb
from flask import Flask, render_template, request, redirect, url_for, Blueprint
from main import db,bcrypt
from models import Document
from forms import UploadForm
from flask_login import login_required, current_user
import pdfplumber 
from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
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
        file=form.document.data
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
        doc=Document(filename=file.filename, user_id=current_user.id,chunk_size=len(chunks),collection_name=collection_name)
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('study.query', doc_id=doc.id))
    return render_template('upload.html', form=form)

def query_llm(doc,query):
    client=chromadb.Client()
    collection=client.get_collection(doc.collection_name)
    results=collection.query(
        query_texts=[query],
        n_results=3,
    )
    chunks=results['documents'][0]
    text="\n\n".join(chunks)
    prompt = f"""You are a study assistant. Answer the question using only the notes below.
If the answer is not in the notes, say "I couldn't find that in your notes."

Notes:{text}

Question: {query}"""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

@study.route('/upload/query/<doc_id>', methods=['GET', 'POST'])
@login_required
def query(doc_id):
    if request.method == 'POST':
        query=request.form.get('query')
        doc=Document.query.get_or_404(doc_id)
        if doc.user_id != current_user.id:
            return "Unauthorized", 403
        answer=query_llm(doc,query)
        return render_template('query.html', doc_id=doc_id, answer=answer, query=query)
    
    return render_template('query.html', doc_id=doc_id)