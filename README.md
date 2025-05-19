# 🧾 POS API Service

A backend service built with **FastAPI** and **SQLite**, designed to power a modern **Point of Sale (POS)** system. The API supports comprehensive store operations such as product management, campaign creation, shift handling, receipt processing, and financial reporting.

---

## 📌 Overview

This service provides a complete backend solution for retail store operations. It supports multiple user roles including store managers, cashiers, and customers. The API enables functionality such as inventory control, sales campaigns, shift tracking, and real-time reporting — all via a simple HTTP interface.

---

## 🧑‍💼 Key Features

### Store Management
- Register and manage goods with dynamic pricing
- Browse product assortments
- Update item prices anytime

### Campaigns & Promotions
- **Discount Campaigns**: Apply percentage-based discounts to specific items or entire receipts
- **Buy N Get N Campaigns**: Reward purchases with additional items (e.g., buy 2 get 1 free)
- **Combo Campaigns**: Offer discounts when specific products are purchased together

### Shift and Transaction Management
- Open and close shifts
- Create and manage receipts
- Add products to receipts and apply active promotions automatically
- Record payments in **GEL**, **USD**, or **EUR** using real-time exchange rates

### Reporting
- **X Reports**: Shift-based summaries including total receipts, items sold, and revenue per currency
- **Sales Reports**: Lifetime store revenue broken down by currency

---

## 👥 User Roles & Stories

### Store Manager
- Manage products and pricing
- Launch marketing campaigns (discounts, combos, buy-n-get-n)
- View real-time and historical sales performance via reports

### Cashier
- Manage daily shifts and receipts
- Add products and apply discounts
- Handle multi-currency payments
- Generate closing reports at end of shift

### Customer
- View itemized receipts with discount breakdowns
- Pay in preferred currency (GEL, USD, EUR)

---

## 💵 Currency & Exchange

- Base pricing is in **GEL** (Georgian Lari)
- Real-time currency conversion is supported via a public exchange rate API (you may integrate your choice of provider)

---

## 📂 API Endpoints (Sample)

Here’s a glimpse of available endpoints:

- `POST /products` – Create a new product  
- `GET /products` – List all products  
- `PATCH /products/{product_id}` – Update product info  
- `POST /campaigns` – Create a new campaign  
- `DELETE /campaigns/{campaign_id}` – Deactivate a campaign  
- `GET /campaigns` – List all active campaigns  
- `POST /receipts` – Start a new receipt  
- `POST /receipts/{receipt_id}/products` – Add product to receipt  
- `POST /receipts/{receipt_id}/quotes` – Calculate total in selected currency  
- `POST /receipts/{receipt_id}/payments` – Register a payment  
- `GET /x-reports?shift_id={shift_id}` – Shift-specific report  
- `GET /sales` – Lifetime sales report  

---

## 🧪 Testing & Code Quality

- All code is formatted and linted using [`ruff`](https://github.com/astral-sh/ruff)
- Type safety is enforced using [`mypy`](http://mypy-lang.org/)
- Includes automated tests to protect against regressions and ensure system reliability

---

## ⚠️ Notes

- No authentication or authorization – all endpoints are unrestricted
- No UI is provided – this is a backend-only service
- SQLite is used for persistent storage

---

## 🧼 Code Expectations

To maintain clean and maintainable code:
- Avoid unnecessary complexity
- Break down logic into small, composable classes and methods
- Eliminate duplication
- Follow SOLID principles and maintain a readable structure

---

## 🗨️ Clarifications

This service is modeled on real-world retail operations. If any requirements appear ambiguous or incomplete, they should be clarified explicitly — assumptions should not be made.
