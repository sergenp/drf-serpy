import os
import pathlib
import sys

# add serpy to path
path = pathlib.Path().parent.parent.absolute()
sys.path.append(str(path))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
