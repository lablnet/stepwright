---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Create template with '...'
2. Run scraper on '....'
3. See error

**Code Example**
```python
# Minimal code to reproduce the issue
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep

async def reproduce():
    templates = [
        TabTemplate(
            tab='test',
            steps=[
                # Your steps here
            ]
        )
    ]
    results = await run_scraper(templates)
    print(results)

asyncio.run(reproduce())
```

**Expected behavior**
A clear and concise description of what you expected to happen.

**Error message/Stack trace**
```
Paste the full error message here
```

**Environment:**
 - OS: [e.g. Ubuntu 22.04, Windows 11, macOS 13]
 - Python version: [e.g. 3.11.0]
 - StepWright version: [e.g. 0.1.0]
 - Playwright version: [e.g. 1.40.0]

**Additional context**
Add any other context about the problem here.

**Screenshots**
If applicable, add screenshots to help explain your problem.

