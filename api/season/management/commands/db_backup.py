import os
import subprocess
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Create a MySQL backup using .env credentials"

    def handle(self, *args, **options):
        # File name: DD-MM-YYYY.sql
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        filename = date.today().strftime("%d-%m-%Y") + ".sql"
        backup_path = os.path.join(backup_dir, filename)

        # Build the mysqldump command using settings from .env
        db = settings.DATABASES['default']
        
        # Check if it's MySQL
        if 'mysql' not in db['ENGINE']:
             # Fallback for SQLite if needed, though the request specifically mentioned MySQL
             if 'sqlite' in db['ENGINE']:
                 import shutil
                 shutil.copy2(db['NAME'], backup_path)
                 self.stdout.write(self.style.SUCCESS(f"SQLite backup saved to {backup_path}"))
                 return
             else:
                 self.stderr.write(self.style.ERROR(f"Backup not supported for engine: {db['ENGINE']}"))
                 return

        cmd = [
            "mysqldump",
            f"-h{db['HOST']}",
            f"-u{db['USER']}",
            f"-p{db['PASSWORD']}",
        ]

        if 'PORT' in db and db['PORT']:
            cmd.append(f"-P{db['PORT']}")

        cmd.append(db['NAME'])

        try:
            with open(backup_path, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            self.stdout.write(self.style.SUCCESS(f"Backup saved to {backup_path}"))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Backup failed: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
