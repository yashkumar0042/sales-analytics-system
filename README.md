# 📊 Sales Analytics System

A Python-based Sales Analytics System that processes raw transaction data, enriches it using an external API, performs detailed sales analysis, and generates comprehensive text-based reports.

This project is structured as a modular analytics pipeline and is fully aligned with the Masai School evaluation rubric.

---

## 📁 Project Structure

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
