### Hexlet tests and linter status:

[![Actions Status](https://github.com/LovichLevich/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)]
[![Maintainability](https://api.codeclimate.com/v1/badges/e996d71e3f298f7a8cc9/maintainability)](https://codeclimate.com/github/LovichLevich/python-project-83/maintainability)

<div style="text-align: center;">
# **Page Analyzer**
</div>

## **Description:**
**Page Analyzer** is a web-based tool designed to analyze and extract useful information from web pages. It fetches data from URLs, parses HTML content, and provides detailed insights about the structure and content of the page. This tool is especially useful for **developers**, **QA specialists**, and **data analysts** who need to analyze websites for performance, SEO, content, or structural quality.

 You can check out the web application at this link:[Page Analyzer ](https://python-project-83-13a1.onrender.com)

## **Installation**
Before you start working with the project, you need to create a **PostgreSQL** database. To create the tables required for work, you can use SQL queries from the **database.sql** file. You also need to create a **.env** file in the root directory of the project and place the environment variables in it:

**SECRET_KEY** - secret key for the session mechanism in Flask.

**DATABASE_URL** - link to connect to the database in the postgresql:// format

## **Using the Application**

- Once the application is running, navigate to the local IP address displayed in the terminal.
  
- On the homepage, you’ll find a field to enter the URL of a website. If the URL is valid, it will be added to the database.

- You can view all the added URLs by clicking on the **"Sites"** tab. Next to each site, the server's response code (200 if the page loaded successfully) is shown, along with the date of the last check.

- Each site has its own dedicated page where you can run checks and view analysis results, such as the presence of **H1** headers and the **meta** tags for **title** and **description**.

- All operational results, including error messages, are displayed at the top of the page as **flash messages**.
