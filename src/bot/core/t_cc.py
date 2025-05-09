import os
from pathlib import Path
from aiogram.types import User

class TelegramClientContext:
    def __init__(self, tg_user: User):
        self.tg_id = tg_user.id
        self.name = tg_user.full_name or "Unknown"
        self.root_folder = Path(os.getenv('PVOL_FOLDER')) / 'clients' /str(self.tg_id)

        self.originals = self.root_folder / 'originals'
        self.bw = self.root_folder / 'bw'
        self.improved = self.root_folder / 'improved'

        self._create_dirs()

    def _create_dirs(self):
        for folder in [self.root_folder, self.originals, self.bw, self.improved]:
            folder.mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return f"<TelegramClientContext {self.tg_id} ({self.name})>"