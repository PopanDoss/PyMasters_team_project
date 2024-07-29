import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import qrcode
from io import BytesIO

from typing import List, Dict

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME', 'default_name'),
    api_key=os.getenv('CLOUDINARY_API_KEY', 'default_key'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET_KEY', 'default_secret')
)

def upload_photo_to_cloudinary(file, public_id=None) -> str:
    """
    Uploads a photo to Cloudinary and returns the URL of the uploaded photo.

    Parameters:
    - file (File-like object): The photo to be uploaded. Should be an object that supports the `read()` method.
    - public_id (str, optional): Public ID for the photo. If not provided, Cloudinary will generate it automatically.

    Returns:
    - str: The URL of the uploaded photo on Cloudinary.
    """
    try:
        result = cloudinary.uploader.upload(file, public_id=public_id)
        return result.get('url')
    except Exception as e:
        print(f"Error uploading photo: {e}")
        raise

def delete_photo_from_cloudinary(photo_url: str):
    """
    Deletes a photo from Cloudinary using the photo URL.

    Parameters:
    - photo_url (str): URL of the photo to be deleted.

    Returns:
    - None: The function does not return a value, but raises an error if something goes wrong.
    """
    try:
        public_id = photo_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Error deleting photo: {e}")
        raise

def create_transformation_urls(photo_url: str, transformations: List[Dict]) -> List[Dict]:
    """
    Generates transformation URLs for Cloudinary and QR codes for each transformation.

    Parameters:
    - photo_url (str): URL of the original photo.
    - transformations (List[Dict]): List of dictionaries describing transformations. Each dictionary should contain:
      - "width" (int): Width of the transformed photo.
      - "height" (int): Height of the transformed photo.
      - "crop" (str): Crop type (e.g., "fill", "fit", "limit").

    Returns:
    - List[Dict]: List of dictionaries where each dictionary contains:
      - "transformation_url" (str): URL of the transformed photo.
      - "qr_code_url" (str): URL of the QR code for the transformed photo.
    """
    base_url = photo_url.split('/upload/')[0] + '/upload'
    transformation_urls = []

    for trans in transformations:
        transformation_string = f"w_{trans['width']},h_{trans['height']},c_{trans['crop']}"
        transformation_url = f"{base_url}/{transformation_string}/{photo_url.split('/upload/')[-1]}"
        qr_code_url = generate_qr_code(transformation_url)
        transformation_urls.append({
            "transformation_url": transformation_url,
            "qr_code_url": qr_code_url
        })

    return transformation_urls

def generate_qr_code(url: str) -> str:
    """
    Generates a QR code for a given URL and uploads it to Cloudinary.

    Parameters:
    - url (str): URL for which the QR code needs to be generated.

    Returns:
    - str: URL of the uploaded QR code on Cloudinary.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        
        buffered = BytesIO()
        img.save(buffered)
        buffered.seek(0)
        
        qr_code_result = cloudinary.uploader.upload(buffered, public_id=f"{url}_qr_code")
        return qr_code_result['url']
    except Exception as e:
        print(f"Error generating QR code: {e}")
        raise

def transform_photo(photo_url: str, transformation: str) -> Dict:
    """
    Applies a single transformation to the photo and generates a QR code for it.

    Parameters:
    - photo_url (str): URL of the original photo.
    - transformation (str): Name of the transformation to apply. E.g., "width_300,height_300,c_fill".

    Returns:
    - Dict: A dictionary containing the URL of the transformed photo and its QR code. If the transformation is not found, returns a dictionary with an error message.
    """
    # Remove quotes if present
    transformation = transformation.strip("'\"")
    
    # List of available transformations
    transformations = [
        {"width": 300, "height": 300, "crop": "fill", "name": "width_300,height_300,c_fill"},
        {"width": 600, "height": 400, "crop": "fit", "name": "width_600,height_400,c_fit"},
        {"width": 800, "height": 800, "crop": "limit", "name": "width_800,height_800,c_limit"}
    ]
    
    # Print debug information
    print(f"Requested transformation: {transformation}")
    print(f"Available transformations: {[trans['name'] for trans in transformations]}")
    
    # Create transformation URLs
    transformation_urls = create_transformation_urls(photo_url, transformations)
    
    # Find the specific transformation URL
    for trans in transformation_urls:
        if transformation in trans["transformation_url"]:
            return trans
    
    return {"error": "Transformation not found"}
