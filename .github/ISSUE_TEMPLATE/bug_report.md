name: 🐛 Bug Report
description: Create a report to help us improve Whisper Voice Dictation AI
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: Describe the bug
      description: A clear and concise description of what the bug is.
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior.
    validations:
      required: true
  - type: textarea
    id: logs
    attributes:
      label: Relevant Log Output (from app.log)
      description: Paste any error stack traces from app.log if available.
    validations:
      required: false
