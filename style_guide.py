
import os
import requests
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import tableauserverclient as TSC

def save_dashboard_image(server, dashboard_luid, image_dir='dashboard_images'):
    """
    Save a dashboard image to disk, skipping if the file already exists.
    
    Args:
        server (TSC.Server): Tableau Server Client instance
        dashboard_luid (str): LUID of the dashboard to save
        image_dir (str): Directory to save the image files
    """

    # Get the absolute path to the folder in the current directory
    folder_path = os.path.join(os.getcwd(), image_dir)

    # Check if the folder exists, if not create folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Check if the image file already exists
    image_path = os.path.join(image_dir, f"{dashboard_luid}.png")
    if os.path.exists(image_path):
        print(f"Skipping image for dashboard LUID: {dashboard_luid} - file already exists.")
        return
    
    try:
        # Get the view and populate the image
        selected_view = server.views.get_by_id(dashboard_luid)
        server.views.populate_image(selected_view)
        
        # Save the image to disk
        os.makedirs(image_dir, exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(selected_view.image)
        
        print(f"Saved image for dashboard LUID: {dashboard_luid}")
    
    except Exception as e:
        print(f"Error saving image for dashboard LUID: {dashboard_luid} - {str(e)}")


# Read Tableau authentication config from environment
tableau_server   = os.getenv('TABLEAU_DOMAIN')   
tableau_site     = os.getenv('SITE_NAME')        
tableau_user     = os.getenv('TABLEAU_USER')     

# Credentials for generating auth token via connnected app
tableau_jwt_client_id    = os.getenv('TABLEAU_JWT_CLIENT_ID')
tableau_jwt_secret_id    = os.getenv('TABLEAU_JWT_SECRET_ID')
tableau_jwt_secret = os.getenv('TABLEAU_JWT_SECRET')
tableau_api_version  = os.getenv('TABLEAU_API_VERSION') 

access_scopes = [
        "tableau:content:read",
        "tableau:viz_data_service:read",
        "tableau:views:download",
        "tableau:workbooks:download"
        "tableau:content:download"
    ]

site_id = tableau_site 

jwt_token = jwt.encode(
        {
        "iss": tableau_jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": access_scopes
        },
        tableau_jwt_secret,
        algorithm = "HS256",
        headers = {
        'kid': tableau_jwt_secret_id,
        'iss': tableau_jwt_client_id
        }
    )

# Create JWTAuth object
tableau_auth = TSC.JWTAuth(jwt=jwt_token, site_id=site_id) 

# Connect to Tableau Server
server = TSC.Server(tableau_server, use_server_version=tableau_api_version)
server.auth.sign_in(tableau_auth)

# Perform operations
print("Signed in successfully!")

server.auth.sign_out()

