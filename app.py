from flask import Flask, render_template, request, send_file, url_for
from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageEnhance, ExifTags
import os
import uuid
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Define folders for uploads and processed images
UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Create sessions for rembg models
MODEL_SESSIONS = {}
MODELS = ["isnet-general-use", "u2net", "isnet-animal"]
for model in MODELS:
    try:
        MODEL_SESSIONS[model] = new_session(model)
    except Exception as e:
        print(f"Failed to load {model} session: {str(e)}")
        MODEL_SESSIONS[model] = None
u2net_session = MODEL_SESSIONS.get("u2net")  # Fallback model

def correct_image_orientation(image):
    """
    Correct image orientation based on EXIF data.
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = image.getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        print(f"Error correcting image orientation: {str(e)}")
    return image

def post_process_image(image):
    """
    Apply post-processing to smooth edges and improve quality.
    """
    img_array = np.array(image)
    if img_array.shape[-1] == 4:  # Ensure RGBA
        alpha = img_array[:, :, 3]
        alpha = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(radius=2))
        img_array[:, :, 3] = np.array(alpha)
    return Image.fromarray(img_array)

def preprocess_image(image, model_type):
    """
    Preprocess image based on the model type.
    """
    # Resize image to a reasonable size for faster processing
    max_size = 512  # Reduced for consistent display
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Enhance contrast and sharpness based on model type
    if model_type == "isnet-animal":
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Sharpness(image).enhance(1.5)
    else:
        image = ImageEnhance.Contrast(image).enhance(1.4)
        image = ImageEnhance.Sharpness(image).enhance(1.2)
    
    return image

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', original_image=None, preview_image=None)

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload, remove background, and show preview."""
    try:
        # Check if a file was uploaded
        if 'image' not in request.files:
            return render_template('index.html', error="No file uploaded", original_image=None, preview_image=None)
        
        file = request.files['image']
        
        # Validate file
        if file.filename == '':
            return render_template('index.html', error="No file selected", original_image=None, preview_image=None)
        
        # Save the original file
        original_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(original_path)
        
        # Open and preprocess the image
        input_image = Image.open(original_path).convert('RGB')
        
        # Correct image orientation
        input_image = correct_image_orientation(input_image)
        
        # Resize the image for processing
        input_image = preprocess_image(input_image, request.form.get('model', 'isnet-general-use'))
        
        # Save the resized original image for display
        original_image = input_image.copy()  # Copy the resized and oriented image
        original_image.save(original_path)   # Overwrite with resized version
        
        # Get selected model
        selected_model = request.form.get('model', 'isnet-general-use')
        session = MODEL_SESSIONS.get(selected_model, u2net_session)
        if not session:
            os.remove(original_path)
            return render_template('index.html', error=f"Model {selected_model} not available", original_image=None, preview_image=None)
        
        # Remove background
        output_image = remove(input_image, session=session)
        
        # Ensure RGBA mode for transparency
        if output_image.mode != 'RGBA':
            output_image = output_image.convert('RGBA')
        
        # Apply post-processing to smooth edges
        output_image = post_process_image(output_image)
        
        # Resize processed image to match original dimensions exactly
        output_image = output_image.resize(input_image.size, Image.Resampling.LANCZOS)
        
        # Save processed image for preview
        output_filename = str(uuid.uuid4()) + '.png'
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        output_image.save(output_path, 'PNG')
        
        # Render preview with both original and processed images
        return render_template('index.html', original_image=original_filename, preview_image=output_filename, error=None)
    
    except Exception as e:
        if 'original_path' in locals() and os.path.exists(original_path):
            os.remove(original_path)
        return render_template('index.html', error=f"Error processing image: {str(e)}", original_image=None, preview_image=None)

@app.route('/download/<filename>')
def download_image(filename):
    """Serve the processed image for download with a unique filename."""
    try:
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(output_path):
            return "File not found", 404
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        unique_filename = f"output_{timestamp}.png"
        
        # Send file for download
        response = send_file(
            output_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=unique_filename
        )
        
        # Clean up both original and processed files
        original_filename = request.args.get('original', None)
        if original_filename:
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            if os.path.exists(original_path):
                os.remove(original_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return response
    except Exception as e:
        return f"Error downloading image: {str(e)}", 500

@app.route('/cancel/<original_filename>/<preview_filename>')
def cancel(original_filename, preview_filename):
    """Clean up files when canceling the preview."""
    try:
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], preview_filename)
        
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return render_template('index.html', original_image=None, preview_image=None)
    except Exception as e:
        return render_template('index.html', error=f"Error canceling: {str(e)}", original_image=None, preview_image=None)

if __name__ == '__main__':
    app.run(debug=True)