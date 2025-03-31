import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
import tableauserverclient as TSC

def authenticate_tableau():
    """
    Authenticate to Tableau Server using JWT authentication.
    
    This function reads the required configuration from environment variables,
    generates a JWT token with the proper access scopes, creates a JWTAuth object,
    and signs into Tableau Server.
    
    Environment Variables Used:
        TABLEAU_DOMAIN         - Tableau Server URL.
        SITE_NAME              - Tableau Site name.
        TABLEAU_USER           - Tableau username.
        TABLEAU_JWT_CLIENT_ID  - JWT client ID.
        TABLEAU_JWT_SECRET_ID  - JWT secret ID.
        TABLEAU_JWT_SECRET     - Secret used for signing the JWT.
        TABLEAU_API_VERSION    - API version to use with the server.
    
    Returns:
        TSC.Server: An authenticated Tableau Server client instance.
    
    Raises:
        Exception: If the authentication fails.
    """
    # Read Tableau authentication config from environment variables
    tableau_server          = os.getenv('TABLEAU_DOMAIN')
    tableau_site            = os.getenv('SITE_NAME')
    tableau_user            = os.getenv('TABLEAU_USER')
    tableau_jwt_client_id   = os.getenv('TABLEAU_JWT_CLIENT_ID')
    tableau_jwt_secret_id   = os.getenv('TABLEAU_JWT_SECRET_ID')
    tableau_jwt_secret      = os.getenv('TABLEAU_JWT_SECRET')
    tableau_api_version     = os.getenv('TABLEAU_API_VERSION')

    # Define the access scopes for the JWT
    access_scopes = [
        "tableau:content:read",
        "tableau:viz_data_service:read",
        "tableau:views:download",
        "tableau:workbooks:download",
        "tableau:content:download"
    ]

    # Create the JWT token with an expiration time of 5 minutes
    jwt_payload = {
        "iss": tableau_jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": access_scopes
    }
    jwt_headers = {
        'kid': tableau_jwt_secret_id,
        'iss': tableau_jwt_client_id
    }
    jwt_token = jwt.encode(jwt_payload, tableau_jwt_secret, algorithm="HS256", headers=jwt_headers)

    # Create a JWTAuth object using the token and site id
    tableau_auth = TSC.JWTAuth(jwt=jwt_token, site_id=tableau_site)
    server = TSC.Server(tableau_server, use_server_version=tableau_api_version)
    
    try:
        server.auth.sign_in(tableau_auth)
        print("Signed in successfully!")
    except Exception as e:
        print(f"Error during Tableau authentication: {e}")
        raise
    
    return server


def save_dashboard_image(server, dashboard_luid, image_dir='dashboard_images'):
    """
    Save a dashboard image to disk, skipping if the file already exists.
    
    Args:
        server (TSC.Server): Tableau Server Client instance.
        dashboard_luid (str): LUID of the dashboard to save.
        image_dir (str): Directory to save the image files.
    """
    folder_path = os.path.join(os.getcwd(), image_dir)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    image_path = os.path.join(image_dir, f"{dashboard_luid}.png")
    if os.path.exists(image_path):
        print(f"Skipping image for dashboard LUID: {dashboard_luid} - file already exists.")
        return
    
    try:
        selected_view = server.views.get_by_id(dashboard_luid)
        server.views.populate_image(selected_view)
        os.makedirs(image_dir, exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(selected_view.image)
        print(f"Saved image for dashboard LUID: {dashboard_luid}")
    except Exception as e:
        print(f"Error saving image for dashboard LUID: {dashboard_luid} - {str(e)}")

