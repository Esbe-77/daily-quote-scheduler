"""Persistent least-recently-shown selection, with random ties for unseen items."""

import hashlib
import json
import os
from pathlib import Path
import random
import unicodedata


def content_id(text):
    # Treat differences in punctuation, case and spacing as the same content.
    normal = unicodedata.normalize('NFKC', text).casefold()
    normal = ' '.join(''.join(c if c.isalnum() else ' ' for c in normal).split())
    return hashlib.sha256(normal.encode('utf-8')).hexdigest()


class Rotation:
    def __init__(self, path='rotation_state.json'):
        self.path = Path(path)
        try:
            self.state = json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            self.state = {'version': 1, 'sequence': 0, 'groups': {}}
        # Never silently reset unreadable history and start repeating content.
        state = self.state
        if (not isinstance(state, dict) or state.get('version') != 1
                or type(state.get('sequence')) is not int or state['sequence'] < 0
                or not isinstance(state.get('groups'), dict)):
            raise ValueError('Invalid rotation history')
        for history in state['groups'].values():
            if not isinstance(history, dict) or any(
                    type(value) is not int or not 0 < value <= state['sequence']
                    for value in history.values()):
                raise ValueError('Invalid rotation history entries')

    def choose(self, group, texts, count=1):
        """Stage selections in memory; save only after SMTP accepts the email."""
        unique = {}
        for index, text in enumerate(texts):
            unique.setdefault(content_id(text), index)
        if not 1 <= count <= len(unique):
            raise ValueError('Selection count must fit the distinct content pool')
        history = self.state['groups'].setdefault(group, {})
        selected = []
        for _ in range(count):
            oldest = min(history.get(key, 0) for key in unique)
            key = random.choice([key for key in unique if history.get(key, 0) == oldest])
            selected.append(unique.pop(key))
            self.state['sequence'] += 1
            history[key] = self.state['sequence']
        return selected

    def save(self):
        temporary = self.path.with_suffix(self.path.suffix + '.tmp')
        temporary.write_text(json.dumps(self.state, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, self.path)
