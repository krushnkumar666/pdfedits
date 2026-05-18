from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import subprocess
import fitz
from pdf2docx import Converter

app = Flask(__name__)

# =========================
# FOLDERS
# =========================

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# =========================
# LIBREOFFICE PATH
# =========================

LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CONVERT PDF
# =========================

@app.route("/convert", methods=["POST"])
def convert_pdf():

    try:

        if "pdf_file" not in request.files:

            return jsonify({
                "success": False,
                "error": "No file uploaded"
            })

        file = request.files["pdf_file"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "error": "No selected file"
            })

        # -------------------------
        # CREATE UNIQUE FILE
        # -------------------------

        unique_id = str(uuid.uuid4())

        pdf_filename = unique_id + ".pdf"

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            pdf_filename
        )

        file.save(pdf_path)

        # -------------------------
        # PAGE COUNT
        # -------------------------

        pdf = fitz.open(pdf_path)

        total_pages = len(pdf)

        pdf.close()

        # -------------------------
        # OUTPUT DOCX
        # -------------------------

        docx_filename = unique_id + ".docx"

        docx_path = os.path.join(
            CONVERTED_FOLDER,
            docx_filename
        )

        # ==================================================
        # FAST LIBREOFFICE CONVERSION
        # ==================================================

        try:

            process = subprocess.run(
                [
                    LIBREOFFICE_PATH,
                    "--headless",
                    "--convert-to",
                    "docx",
                    pdf_path,
                    "--outdir",
                    CONVERTED_FOLDER
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120
            )

            generated_docx = os.path.join(
                CONVERTED_FOLDER,
                os.path.splitext(pdf_filename)[0] + ".docx"
            )

            if os.path.exists(generated_docx):

                if generated_docx != docx_path:

                    if os.path.exists(docx_path):
                        os.remove(docx_path)

                    os.rename(
                        generated_docx,
                        docx_path
                    )

            else:

                # Fallback
                cv = Converter(pdf_path)

                cv.convert(docx_path)

                cv.close()

        except Exception as e:

            # FALLBACK METHOD
            cv = Converter(pdf_path)

            cv.convert(docx_path)

            cv.close()

        # -------------------------
        # SUCCESS
        # -------------------------

        return jsonify({
            "success": True,
            "download_url": f"/download/{unique_id}",
            "pages": total_pages,
            "filename": file.filename
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================
# DOWNLOAD
# =========================

@app.route("/download/<file_id>")
def download(file_id):

    path = os.path.join(
        CONVERTED_FOLDER,
        file_id + ".docx"
    )

    if os.path.exists(path):

        return send_file(
            path,
            as_attachment=True,
            download_name="converted.docx"
        )

    return "File Not Found"


# =========================
# CLEAR FILES
# =========================

@app.route("/clear", methods=["POST"])
def clear_files():

    try:

        for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:

            for file in os.listdir(folder):

                path = os.path.join(folder, file)

                if os.path.isfile(path):
                    os.remove(path)

        return jsonify({
            "success": True
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )