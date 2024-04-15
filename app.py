from flask import Flask, request, jsonify, render_template, send_file, redirect
import zipfile
import os
from process_data import process_files
import uuid

app = Flask(__name__)

# path is currect working director + /tmp

app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "tmp")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process-zip", methods=["POST"])
def process_zip():
    # if "zip_file" not in request.files:
    #     return jsonify({"error": "No zip_file provided"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    zip_file = request.files["file"]

    if zip_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if zip_file:
        try:
            # Save the zip file temporarily
            zip_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], "extracted.zip"
            )  # Change the path as needed
            zip_file.save(zip_file_path)

            unique_id = str(uuid.uuid4())

            # Extract the zip file
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(
                    os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted")
                )  # Change the extraction path as needed

            # Process the extracted files here
            output_file = os.path.join(
                app.config["UPLOAD_FOLDER"], f"{unique_id}-output.xlsx"
            )
            process_files(
                os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted"),
                output_file,
            )

            # Delete the temporary zip file
            os.remove(zip_file_path)
            for folder in os.listdir(
                os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted")
            ):
                for file in os.listdir(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted", folder
                    )
                ):
                    os.remove(
                        os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            f"{unique_id}-extracted",
                            folder,
                            file,
                        )
                    )
                os.rmdir(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted", folder
                    )
                )
            os.rmdir(
                os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}-extracted")
            )

            return redirect(f"/success/{unique_id}")
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Invalid request"}), 400


@app.route("/success/<unique_id>")
def success(unique_id):
    return render_template("success.html", unique_id=unique_id)


@app.route("/download/<unique_id>")
def download(unique_id):
    return send_file(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}-output.xlsx"),
        as_attachment=True,
        download_name="resume_data.xlsx",
    )


if __name__ == "__main__":
    app.run(debug=True)
