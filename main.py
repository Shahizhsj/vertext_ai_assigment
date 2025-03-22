from flask import Flask, request, jsonify
import google.generativeai as genai
import time
import os

app = Flask(__name__)

# Configure Gemini AI
GOOGLE_API_KEY = "AIzaSyC6TmVb5Vk5J0r6z0oCmjvNgzbblDKuf3Y"
genai.configure(api_key=GOOGLE_API_KEY)

def process_file(file_path, file_name="abcde"):
    """
    Uploads a file to Gemini AI, waits for processing, and retrieves results.
    """
    try:
        pdfFile = genai.get_file(f"files/{file_name}")
    except:
        pdfFile = genai.upload_file(path=file_path, name=file_name, resumable=True)

    # Wait until the file is processed
    while pdfFile.state.name == "PROCESSING":
        time.sleep(10)
        pdfFile = genai.get_file(pdfFile.name)

    if pdfFile.state.name == "FAILED":
        return {"error": "File processing failed."}

    model = genai.GenerativeModel(
        model_name="models/gemini-2.0-flash",
        system_instruction=["Analyze this file"]
    )
    
    response = model.generate_content([pdfFile, "Analyze this document"], request_options={"timeout": 600})
    return {"analysis_result": response.text}

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    API endpoint to receive a file and process it using Gemini AI.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    # Save the uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    # Process the file
    result = process_file(temp_path)

    # Remove the temporary file
    os.remove(temp_path)

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
