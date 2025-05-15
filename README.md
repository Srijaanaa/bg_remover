# Background Remover

A simple web application built with Flask that allows users to upload images and remove their backgrounds using the `rembg` library. The app supports multiple models for different types of images (e.g., general objects, human portraits, animals) and provides a downloadable processed image.

## Features
- Upload any image and remove its background.
- Choose from multiple pre-trained models (e.g., `isnet-general-use`, `u2net`, `isnet-animal`).
- Preview both original and processed images.
- Download the processed image with a transparent background.
- Responsive design with a modern, gradient-styled interface.

## Prerequisites
- **Python**: Version 3.11 or 3.12 recommended.
- **pip**: Python package manager.
- **Homebrew** (for macOS): For installing Python if needed.
- A web browser (e.g., Chrome, Firefox) to access the app.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/bg-remover.git
cd background-remover
```

### 2. Set Up a Virtual Environment
- For Python 3.12 (recommended):
  ```bash
  python3.12 -m venv virtual
  source virtual/bin/activate
  ```
- For Python 3.11 (alternative):
  ```bash
  brew install python@3.11
  /opt/homebrew/bin/python3.11 -m venv virtual
  source virtual/bin/activate
  ```

### 3. Install Dependencies
Run the following command to install required packages:
- For Python 3.12:
  ```bash
  pip install --upgrade pip
  pip install rembg onnxruntime opencv-python-headless==4.10.0.84 numpy==2.2.5 pillow==11.2.1 flask
  ```
- For Python 3.11:
  ```bash
  pip install rembg==2.0.57 onnxruntime==1.20.0 opencv-python-headless==4.10.0.84 numpy==2.2.5 pillow==11.2.1 flask
  ```

### 4. Run the Application
```bash
python app.py
```
Open your browser and go to `http://127.0.0.1:5000` to use the app.

## Usage
1. **Upload an Image**: Click the "Choose File" button and select an image (any format supported by the browser).
2. **Select a Model**: Choose a model from the dropdown (e.g., "General Objects" for products, "Human Portraits" for people, "Animals" for pets).
3. **Process the Image**: Click "Remove Background" to process the image.
4. **Preview and Download**: View the original and processed images. Click "Download" to save the processed image or "Cancel" to discard it.

## Customization
- **Styles**: Modify `static/css/style.css` to change colors, fonts, or layout. The current design uses a `Poppins` font and a gradient background.
- **Models**: Update the `select` options in `index.html` or the backend logic in `app.py` to add more `rembg` models.
- **Image Size**: Adjust the `.preview-image` class in `style.css` to change the displayed image size.

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. For major changes, please open an issue first to discuss.

## Contact
For support or questions, please open an issue on the [GitHub repository](https://github.com/Srijaanaa/background-remover) or contact the maintainer at srijanalohani02@.com.

