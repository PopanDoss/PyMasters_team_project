import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import qrcode
from io import BytesIO

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET_KEY')
)

def upload_photo_to_cloudinary(file, public_id=None):
    """Upload photo to Cloudinary."""
    result = cloudinary.uploader.upload(file, public_id=public_id)
    return result.get('url')

def delete_photo_from_cloudinary(photo_url):
    """Delete photo from Cloudinary."""
    public_id = photo_url.split('/')[-1].split('.')[0]
    cloudinary.uploader.destroy(public_id)

def create_transformation_urls(photo_url, transformations):
    """Generate transformation URLs for Cloudinary and QR codes."""
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

def generate_qr_code(url):
    """Generate a QR code for a given URL and upload it to Cloudinary."""
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
    img.save(buffered, format='PNG')
    buffered.seek(0)
    
    qr_code_result = cloudinary.uploader.upload(buffered, public_id=f"{url}_qr_code")
    return qr_code_result['url']

def transform_photo(photo_url: str, transformation: str) -> dict:
    """Apply a single transformation to the photo and generate QR code for it."""
    # Remove quotes just in case
    transformation = transformation.strip("'\"")
    
    # List of transformations
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





