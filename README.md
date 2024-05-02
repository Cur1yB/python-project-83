### Hexlet tests and linter status:
[![Actions Status](https://github.com/Cur1yB/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Cur1yB/python-project-83/actions)


# Page Analyzer

Page Analyzer is a Flask web application that allows users to analyze web pages for SEO effectiveness. The application checks the availability of websites and analyzes elements such as headers, descriptions, and H1 tags.

## Features

- URL availability check.
- Analysis of title and description tags.
- Display of check results on the user interface.

## Demo

You can view the application in action at this link:
[Page Analyzer Demo](https://python-project-83-iiur.onrender.com)

## Technologies

- Python
- Flask
- PostgreSQL
- HTML/CSS
- Bootstrap for frontend
- Poetry for dependency management

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have Python, Poetry, and PostgreSQL installed.

### Installation and Running

Use the `Makefile` to simplify the installation and startup process:

```bash
git clone https://github.com/Cur1yB/python-project-83.git
cd python-project-83

# Install dependencies
make install

# Run the local development server
make dev

# Run the production server
make start
```

### Testing

To run tests, use the following command:

```bash
make lint  # Code linting
```
