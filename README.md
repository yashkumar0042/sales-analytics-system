#  Sales Analytics System

A Python-based Sales Analytics System that processes raw transaction data, enriches it using an external API, performs detailed sales analysis, and generates comprehensive text-based reports.

This project is structured as a modular analytics pipeline and is fully aligned with the Masai School evaluation rubric.

---

##  Project Structure

```text
sales-analytics-system/
│
├── main.py
├── README.md
│
├── data/
│   ├── sales_data.txt
│
├── output/
│   └── sales_report.txt
│
└── utils/
    ├── __init__.py
    ├── file_handler.py
    ├── parser.py
    ├── validator.py
    ├── data_processor.py
    ├── api_handler.py
    └── report_generator.py


## Module Responsibilities

| File | Description |
|-----|-------------|
| `main.py` | Main execution flow |
| `file_handler.py` | Read and write sales data files |
| `parser.py` | Parse raw transaction records |
| `validator.py` | Validate and filter transactions |
| `data_processor.py` | Perform sales analytics (revenue, regions, products, customers) |
| `api_handler.py` | API integration and sales data enrichment |
| `report_generator.py` | Generate comprehensive sales report |

---

##  Prerequisites

- Python **3.8 or higher**
- Active internet connection (for DummyJSON API)
- Required dependency:

---

##  How to Execute the Project

### Step 1: Navigate to Project Root


>  Important: Always run the program from the **project root directory**, not from inside the `utils/` folder.

---

### Step 2: Verify Input Data

Ensure the following file exists:



---

### Step 3: Run the Application



**Report includes:**
1. Header (Title, Timestamp, Record Count)
2. Overall Sales Summary
3. Region-wise Performance
4. Top 5 Products
5. Top 5 Customers
6. Daily Sales Trends
7. Product Performance Analysis
8. API Enrichment Summary

---

##  Error Handling

- Gracefully handles invalid or malformed records
- API failures do not crash the program
- Invalid transactions are skipped with summary counts
- User-friendly console messages throughout execution

---

##  Common Issues & Fixes

###  ModuleNotFoundError

Ensure:
- `utils/__init__.py` exists
- The program is executed from the project root directory

---

###  API Connection Issues

Ensure:
- Internet connection is active
- DummyJSON API is reachable

---

##  Final Notes

- Modular and scalable code structure
- Clean separation of concerns
- Fully compliant with Masai assessment requirements
- Easy to extend with additional analytics and reporting

---
