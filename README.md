# SKU Dashboard

This project is a web application built with Django (backend) and Vue.js (frontend) to manage and visualize SKU data. It provides a dashboard to view SKU performance metrics, filter and search SKUs, and add follow-up notes with role-based access control.

## Table of Contents

- [Setup Instructions](#1-setup-instructions)
- [API Routes and Expected Inputs/Outputs](#2-api-routes-and-expected-inputsoutputs)
- [Assumptions Made](#3-assumptions-made)
- [Next Steps (If More Time)](#4-next-steps-if-more-time)
- [Deploying on Render](#5-deploying-on-render)

---

## 1. Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

Note: If you have Python installed but available as `python3`, replace `python` in all the following commands with `python3`.

### 1. Clone the Repository

```
git clone https://github.com/amangarg078/merch.git
cd merch
```

### 2. Create and Activate a Virtual Environment

```
python -m venv env
```
or
```
python3 -m venv env

```

- On Windows:  
  ```
  .\env\Scripts\activate
  ```

- On macOS/Linux:  
  ```
  source env/bin/activate
  ```

### 3. Install Dependencies

```
pip install -r requirements.txt
```


### 4. Database Setup

```
python manage.py migrate
```
or
```
python3 manage.py migrate

```


### 5. Load Mock Data

```
python manage.py load_dummy_data
```
or
```
python3 manage.py load_dummy_data

```

This does the following:
- Create a group named `merch_ops` – can view all notes.
- Create a group named `brand_user` – can add/edit their own notes.
- Create a user named `merchops1` – can view all notes.
- Create a user named `branduser1` – can add/edit their own notes.
- Create a superuser named `admin` - can view the admin console.
- Load dummy data for SKU, metrics, and notes.

### 6. Run the Development Server

```
python manage.py runserver
```
or
```
python3 manage.py runserver

```

Visit `http://127.0.0.1:8000/`

---

## 2. API Routes and Expected Inputs/Outputs

The following apis will work browser as well as any API tool like Postman, cURL, etc.
If using browsers, you just need to make sure that you are logged in to the application, headers will be taken care of automatically.

### 1. List SKUs

**GET** `/api/skus/`

**Query Parameters:**

- `page`, `page_size`
- `search`
- `filter_type` (e.g., `high_return_rate`, `low_content_score`)
- `ordering`

**Example Request:**

```
GET /api/skus/?page=1&page_size=10&search=dress&filter_type=high_return_rate&ordering=-sales'
```

**Example Response:**

```
{
  "count": 2,
  "results": [
    {
      "sku_id": "SKU001",
      "name": "Summer Dress",
      "sales": 1500,
      "return_percentage": 7.5,
      "content_score": 5.2,
      "notes": [], 
      "daily_metrics": [
        {"date": "2024-01-01", "sales_units": 10},
        {"date": "2024-01-02", "sales_units": 15}
      ]
    }
  ]
}
```

### 2. Retrieve SKU Details

```
GET /api/skus/<sku_id>/
```

**Example Response:**

```
{
  "sku_id": "SKU001",
  "name": "Summer Dress",
  "sales": 1500,
  "return_percentage": 7.5,
  "notes": [
    {
      "text": "Customer feedback indicates sizing issues.",
      "created_by_username": "admin"
    }
  ],
  "daily_metrics": [
    {"date": "2024-03-01", "sales_units": 5},
    {"date": "2024-03-02", "sales_units": 8},
    {"date": "2024-03-03", "sales_units": null}
  ]
}
```

### 3. Create a Note

```
POST /api/skus/<sku_id>/notes/
```

**Headers:**

- `Content-Type: application/json`
- `Authorization: Token <your_api_token>`

You can get the api token for every user from `/admin/authtoken/tokenproxy/`.

**Body:**

```
{
  "text": "Investigate supplier for quality control issues."
}
```

### 4. Retrieve/Update Note

```
GET /api/notes/<note_id>/
PATCH /api/notes/<note_id>/
PUT /api/notes/<note_id>/
```

**Headers:**

- `Content-Type: application/json`
- `Authorization: Token <your_api_token>`

**PUT Example:**

```
PUT /api/notes/102/
Content-Type: application/json
Authorization: Token <your_api_token>

{
  "text": "Updated note: Supplier contacted, awaiting response."
}
```

---

## 3. Assumptions Made

- **Database**: SQLite in dev; adaptable to other DBs, preferably Postgres
- **Auth**: Django's default system.
- **Groups**:
  - `merch_ops`: View all notes.
  - `brand_user`: Create/edit own notes.
- **Filters**: Thresholds for return rate/content score are hardcoded.
- **Frontend**:
  - Chart.js via CDN.
  - Vue.js via CDN.
  - Axios for API calls.
- **Metrics**: Raw daily data, aggregated client-side.
- **Auto-save**: Single "active" note per user per SKU.

---

## 4. Next Steps (If More Time)

### Backend

- Add chart data aggregation at the API level, so that we can have more flexibility to view chart data (monthly, weekly, daily trends over a specified time range)
- Use `django-allauth` for social logins, provide a better experience with features like password reset, etc.
- Add:
  - Unit tests
  - Frontend tests
- Expand mock data generator.
- Optimize DB with indexes for faster and efficient searching and filtering.

### Frontend

- Migrate to full Vue build with Vite/Vue CLI.


---

## 5. Deploying on Render

- Create a new **Postgres** database that is remotely accessible. Use Render/Supabase/any cloud service and copy its URL.
- Create a new **web service** on Render, point it this repo.
- Select `Python 3` for the Language and set the following properties:

Property | Value
--- | --- 
Build command | `./build.sh`
Start comman | `python -m gunicorn merch.asgi:application -k uvicorn.workers.UvicornWorker`

- Add the following environment variables under Advanced:

Key | Value
--- | ---
DATABASE_URL | The database URL for the database you created above
SECRET_KEY| Click Generate to get a secure random value
WEB_CONCURRENCY | 4
DEBUG | False

That's it! Save your web service to deploy your Django application on Render. It will be live on your `.onrender.com` URL as soon as the build finishes.
