# SQL Visualizer - Oracle SQL Schema Visualization Tool

Visualize Oracle SQL query structures as ERP-style entity-relationship diagrams with tables, columns, and relationship connections.

## Overview

SQL Visualizer is a Python tool that converts database schemas and SQL queries into interactive diagrams. Perfect for:
- 📊 Database architecture documentation
- 🔍 Understanding complex query structures  
- 📈 Visualizing relationships between tables
- 🎨 Creating ERD-style diagrams automatically

## Features

✨ **Key Capabilities:**
- Create table structures with columns and data types
- Mark Primary Keys (🔑) and Foreign Keys (🔗)
- Define relationships between tables (1:1, 1:N, N:N)
- Generate interactive HTML visualizations
- Export to PNG using Graphviz (optional)
- Support for Oracle SQL syntax

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/sql-visualizer.git
cd sql-visualizer

# Optional: Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from sql_visualizer import SQLSchemaVisualizer, Table, Column, Relationship, KeyType

# Create visualizer
viz = SQLSchemaVisualizer()

# Define tables
users = Table(name="users", alias="u")
users.add_column(Column("user_id", "NUMBER", KeyType.PRIMARY, False))
users.add_column(Column("username", "VARCHAR2(50)", KeyType.NONE, False))

# Add to visualizer
viz.add_table(users)

# Generate output
viz.print_schema()
viz.generate_html("diagram.html")  # Interactive HTML
viz.generate_graphviz("diagram")   # PNG (requires graphviz)
```

## Examples

### E-Commerce Schema
- Customers
- Orders
- Order Items
- Products

### HR Management
- Employees
- Departments
- Jobs
- Locations

### University System
- Students
- Courses
- Enrollments
- Professors

See `sql-visualizer-demo.ipynb` for full working examples.

## API Reference

### SQLSchemaVisualizer
Main class for managing schemas and generating visualizations.

**Methods:**
- `add_table(table: Table)` - Add a table
- `add_relationship(rel: Relationship)` - Add relationship
- `print_schema()` - Console output
- `generate_graphviz(filename, view=False)` - PNG export
- `generate_html(filename)` - HTML export

### Table
Represents a database table.

**Constructor:**
```python
Table(name: str, alias: str = None)
```

### Column
Represents a table column.

**Constructor:**
```python
Column(
    name: str,
    data_type: str,
    key_type: KeyType = KeyType.NONE,
    nullable: bool = True
)
```

### Relationship
Represents table relationships.

**Constructor:**
```python
Relationship(
    from_table: str,
    from_column: str,
    to_table: str,
    to_column: str,
    relationship_type: str = "1:N"
)
```

## Output Formats

### HTML Output
- Interactive visualization with physics simulation
- Pan, zoom, and drag support
- Browser-based (no installation needed)
- Works with Vis.js library

### PNG Output (Graphviz)
- Professional ERD diagrams
- High-quality raster graphics
- Requires graphviz system package

## Installation Guide

### System Dependencies

**Windows:**
```bash
# Download from https://graphviz.org/download/
# Or use Chocolatey:
choco install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install graphviz
```

## Project Structure

```
sql-visualizer/
├── sql_visualizer.py           # Main library
├── sql-visualizer-demo.ipynb   # Example notebook
├── README.md                   # This file
├── requirements.txt            # Dependencies
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

## Requirements

- Python 3.7+
- graphviz (system package, optional for PNG export)

Python packages (see requirements.txt):
- graphviz (for PNG output, optional)

## Usage Examples

### Create E-Commerce Schema

```python
viz = SQLSchemaVisualizer()

# Create tables
customers = Table(name="customers")
customers.add_column(Column("customer_id", "NUMBER", KeyType.PRIMARY, False))
customers.add_column(Column("name", "VARCHAR2(100)", KeyType.NONE, False))

orders = Table(name="orders")
orders.add_column(Column("order_id", "NUMBER", KeyType.PRIMARY, False))
orders.add_column(Column("customer_id", "NUMBER", KeyType.FOREIGN, False))

# Add to visualizer
viz.add_table(customers)
viz.add_table(orders)

# Define relationship
viz.add_relationship(Relationship(
    "customers", "customer_id",
    "orders", "customer_id",
    "1:N"
))

# Generate diagram
viz.print_schema()
viz.generate_html("ecommerce.html")
```

### Parse SQL Query

```python
sql_query = """
SELECT c.*, o.* 
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
"""

viz = SQLSchemaVisualizer()
viz.parse_simple_sql(sql_query)  # Extracts tables and joins
viz.print_schema()
```

## Key Types

- **🔑 PRIMARY** - Primary key, uniquely identifies row
- **🔗 FOREIGN** - Foreign key, references another table
- **Unique** - Unique constraint column
- **Regular** - Standard column

## Troubleshooting

### Graphviz not found
```
Error: "dot" not found in path
```
**Solution:** Install graphviz system package (not Python package)

### HTML looks plain
Normal behavior. Open in modern browser (Chrome, Firefox, Safari, Edge).

### Large schema visualization
For 50+ tables, consider:
- Splitting into multiple views
- Using HTML instead of PNG
- Grouping related tables

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## License

MIT License - see LICENSE file for details

## Changelog

### v1.0.0 (2026-03-15)
- Initial release
- HTML and Graphviz visualization
- Support for Oracle SQL syntax
- Example schemas included

## Support

For issues or questions:
1. Check examples in notebook
2. Review API documentation above
3. File an issue on GitHub

## Author

Created for Oracle SQL schema visualization and analysis.

---

**Transform your SQL schemas into beautiful diagrams!**
