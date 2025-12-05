# Personal Tools

This project captures packages and libraries I typically install in all my projects.


## Current Process
- Initiate libraries and tools required to use python = ./setup.sh
- Update requirements-dev.txt to include packages expected to work with python for scripting in projects.
  - Current Functions:

    # Initialize project
    - uv run bootstrap.py init

    # Install requirements with custom timeout
    - uv run bootstrap.py install-reqs --timeout 600

    # Install from different file
    - uv run bootstrap.py install-reqs --file requirements.txt

    # Run with verbose logging
    - uv run bootstrap.py -vv install-reqs

    # Demo functionality
    - uv run bootstrap.py demo

    Note:
      - These should be contained in the Taskfile.yml.


The decision to share my approach to doing this was inspired by templates used by others to solve a similar problem, with the most noteable being:
  - https://gist.github.com/mrjk/8ae4f22e21c7ab5a57a462db046ad776
  - https://github.com/ralish/bash-script-templatehttps://github.com/ralish/bash-script-template
  - https://go.dev/blog/gonew
