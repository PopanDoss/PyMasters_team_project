# PyMasters Team Project

## Description

**PyMasters Team Project** is a web application built with FastAPI that allows users to upload, edit, and view photos, as well as leave comments. The application supports authentication using JWT tokens and provides different access levels for users, moderators, and administrators.

## Features

### Authentication

- Uses JWT tokens for authentication.
- Three user roles: regular user, moderator, and administrator.
- The first user in the system is automatically assigned as an administrator.
- Uses FastAPI decorators to check tokens and user roles.

### Photo Management

- Upload photos with descriptions (POST).
- Delete photos (DELETE).
- Edit photo descriptions (PUT).
- Retrieve photos via unique links (GET).
- Add up to 5 tags per photo. Tags are unique across the application.
- Photo transformations using Cloudinary.
- Generate links and QR codes for transformed images.
- Store links on the server for later viewing.

### Commenting

- Users can leave comments under photos.
- Users can edit their own comments.
- Administrators and moderators can delete comments.
- Store creation and editing timestamps for comments.

## Setup and Installation

### Requirements

- Python 3.9+
- PostgreSQL
- Docker

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/PopanDoss/PyMasters_team_project.git
   ```

2. Navigate to the project directory:
   ```bash
   cd PyMasters_team_project
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Unix
   venv\Scripts\activate      # For Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables. Create a `.env` file in the root directory and add the following:
   ```
   SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://mydata:mydata@localhost:5432/
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   CLOUDINARY_NAME=your_cloudinary_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET_KEY=your_cloudinary_api_secret_key
   MAIL_USERNAME=your_mail_username
   MAIL_PASSWORD=your_mail_password
   MAIL_FROM=your_mail_from
   ```

6. Start the server using Docker:
   ```bash
   docker-compose up --build
   ```

7. Apply database migrations:
   ```bash
   docker-compose exec web alembic upgrade head
   ```

### Testing

- Run tests:
  ```bash
  pytest
  ```

## Deployment

For deployment on your chosen cloud service, follow the platform's documentation. It is recommended to use Koyeb or Fly.io.

## Authors

- SERHII CHERNENKO
- ANASTASIIA KRASEVYCH
- VALENTYN PIROHOV
- IRYNA SINCHUK
