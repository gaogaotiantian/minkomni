import inspect
import os

from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates


def local_file_path(filename: str): 
    prev_frame = inspect.stack()[1]
    file_dir = os.path.dirname(prev_frame.filename)
    return os.path.join(file_dir, filename)

def local_file(filename: str,
               templated: bool = False,
               context: dict = None):
    prev_frame = inspect.stack()[1]
    file_dir = os.path.dirname(prev_frame.filename)
    template_path = os.path.join(file_dir, "templates")
    if templated:
        templates = Jinja2Templates(
            directory=template_path
        )
        return templates.TemplateResponse(filename, context)
    else:
        return FileResponse(os.path.join(template_path, filename))
