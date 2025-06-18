# NoteShare Project

A Django-based study notes repository system with multi-language support and file sharing capabilities.

## Features

- User roles (visitor, registered user, administrator)
- File upload support (PDFs/images)
- Multi-language support (English and Latvian)
- Bootstrap-based responsive design
- PostgreSQL database backend

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- GNU gettext (for translations)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd noteshare_project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django psycopg2-binary django-bootstrap5
```

4. Configure PostgreSQL:
- Create a database named `noteshare_db`
- Update database credentials in `noteshare_project/settings.py`

5. Create necessary directories:
```bash
mkdir static media locale
```

6. Apply migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Install GNU gettext:
- Windows: Download from https://mlocati.github.io/articles/gettext-iconv-windows.html
- Linux: `sudo apt-get install gettext`
- macOS: `brew install gettext`

9. Generate translation files:
```bash
django-admin makemessages -l lv
django-admin compilemessages
```

## Running the Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your web browser.

## Project Structure

- `notes_core/` - Main application directory
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
- `media/` - User-uploaded files
- `locale/` - Translation files

## Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 