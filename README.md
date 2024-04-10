# Fixed Width File Handler

## Introduction
This library is designed to manipulate fixed-width text files, providing functionality to read, write, and update records in a consistent and structured format.

## Interface
This repository offers also CLI app for managing files.

## Features
- Read and parse fixed-width files into Python data structures.
- Write data back into a fixed-width file format.
- Add new records with automatic incrementation and formatting.
- Update existing records while maintaining file integrity.
- Validation of file format
- Unit Tests
## Quick Start
To get started just run following line

```bash
python main.py {action} {filepath}
```

### For example:
```bash
python main.py read sample.txt
```

## Possible actions
- read - display contents of file
- add - insert new transaction
- update - update specified field
- settings - change possibility to update fields
