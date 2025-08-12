# Basic AI Auto Assistant

## OCR configuration

The watcher thread polls a region of the screen and extracts text using an OCR
backend.  A strategy pattern is employed so different OCR engines can be used.
By default the `PytesseractOCR` backend is selected which relies on the
[pytesseract](https://pypi.org/project/pytesseract/) library.

### Default backend

```
from queue import Queue
from quiz_automation.config import Settings
from quiz_automation.watcher import Watcher

watcher = Watcher((0, 0, 100, 100), Queue(), Settings())
```

The above uses `PytesseractOCR` automatically.  It can be configured with
language options if required:

```
from quiz_automation.ocr import PytesseractOCR

ocr = PytesseractOCR(lang="eng")
watcher = Watcher((0, 0, 100, 100), Queue(), Settings(), ocr=ocr)
```

### Custom backends

Any callable following the `OCRBackend` protocol (`__call__(image) -> str`) can
be supplied to `Watcher` to integrate alternative OCR engines.
