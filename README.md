### Hexlet tests and linter status:

[![Actions Status](https://github.com/LovichLevich/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)]
[![Maintainability](https://api.codeclimate.com/v1/badges/e996d71e3f298f7a8cc9/maintainability)](https://codeclimate.com/github/LovichLevich/python-project-83/maintainability)

### Hexlet tests and linter status:

[![Actions Status](https://github.com/LovichLevich/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/LovichLevich/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/e996d71e3f298f7a8cc9/maintainability)](https://codeclimate.com/github/LovichLevich/python-project-83/maintainability)

# **Page Analyzer**

## **Description:**
**Page Analyzer** is a web-based tool designed to analyze and extract useful information from web pages. It fetches data from URLs, parses HTML content, and provides detailed insights about the structure and content of the page. This tool is especially useful for **developers**, **QA specialists**, and **data analysts** who need to analyze websites for performance, SEO, content, or structural quality.

You can check out the web application at this link: [Page Analyzer](https://python-project-83-13a1.onrender.com)

---

## **Installation and Setup**

### **1. Clone the Repository:**
```bash
git clone <repository>
cd <project folder>

```

### **2. Set Up the Environment with UV:**
Ensure you have **Python ^3.10** and `uv` installed:

```bash
# Install uv if not already installed
pip install uv
```

Create a virtual environment and install dependencies using pyproject.toml:

```bash
uv venv
uv pip sync
```

### **3. Set Up Environment Variables:**
Create a `.env` file in the root directory and define the following variables:

```plaintext
# .env file example
SECRET_KEY="your_secret_key_here"
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
FLASK_APP=app.py
FLASK_ENV=development
```

### **4. Database Setup:**
Create a **PostgreSQL** database and use the SQL queries from the `database.sql` file to create the required tables.

```bash
psql -U <username> -d <database_name> -f database.sql
```

### **5. Run the Application:**
Launch the application using **Uvicorn**:

```bash
make start
```

---

## **Using the Application**

- Once the application is running, navigate to the local IP address displayed in the terminal.
- On the homepage, enter the URL of a website. If valid, it will be added to the database.
- View all added URLs by clicking on the **"Sites"** tab. Next to each site, you’ll see:
  - Server response code (e.g., **200** for successful loads)
  - Date of the last check
- Each site has its own page where you can:
  - Run site checks
  - View analysis results (presence of **H1** headers, **meta** tags for **title** and **description**)
- All results and error messages are displayed at the top of the page as **flash messages**.

---

## **6. Linting and Code Quality (Ruff)**
Run **Ruff** for linting and formatting:

```bash
ruff check .
ruff check . --fix
ruff format .
```

---

