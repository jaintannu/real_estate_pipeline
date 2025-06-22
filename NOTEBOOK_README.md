# 📊 Real Estate Data Analysis Notebook

A comprehensive Jupyter notebook for analyzing real estate data with PostgreSQL integration, statistical analysis, machine learning, and interactive visualizations.

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
cd real_estate_pipeline
python setup_notebook.py
```

### Option 2: Manual Setup
```bash
# Install requirements
pip install -r requirements_notebook.txt

# Launch Jupyter
jupyter notebook Real_Estate_Analysis_Complete.ipynb
```

## 📋 Features

### 🔗 Database Integration
- **Secure PostgreSQL Connection**: Uses SQLAlchemy with connection pooling
- **Automatic Reconnection**: Built-in connection health checks
- **Environment Variables**: Supports DATABASE_URL configuration
- **Error Handling**: Graceful degradation when database unavailable

### 📊 Data Analysis
- **Data Quality Assessment**: Missing value analysis, data profiling
- **Statistical Summaries**: Descriptive statistics for all numeric columns
- **Correlation Analysis**: Heatmaps and correlation significance testing
- **Hypothesis Testing**: ANOVA, t-tests, and statistical inference

### 📈 Visualizations
- **Interactive Charts**: Plotly-powered histograms, scatter plots, pie charts
- **Statistical Plots**: Correlation heatmaps with seaborn
- **Price Analysis**: Distribution analysis and trend visualization
- **Property Comparisons**: Type-based analysis and geographic insights

### 💰 Market Analysis
- **Price Segmentation**: Quartile-based market segments
- **City Analysis**: Geographic price comparisons
- **Investment Insights**: Price per square foot analysis
- **Value Opportunities**: Identification of undervalued markets

## 🛠️ Requirements

### Core Libraries
```
pandas>=1.5.0          # Data manipulation
numpy>=1.21.0          # Numerical computing
scipy>=1.9.0           # Statistical analysis
```

### Database
```
sqlalchemy>=1.4.0      # Database ORM
psycopg2-binary>=2.9.0 # PostgreSQL adapter
```

### Visualization
```
matplotlib>=3.5.0      # Static plots
seaborn>=0.11.0        # Statistical visualization
plotly>=5.10.0         # Interactive charts
folium>=0.12.0         # Geographic mapping
```

## 🔧 Configuration

### Database Connection
The notebook supports multiple connection methods:

1. **Environment Variable** (Recommended):
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

2. **Default Local Connection**:
   ```
   postgresql://postgres:password@localhost:5432/real_estate_db
   ```

3. **Custom Connection String**:
   Modify the connection string directly in the notebook

### Environment Setup
```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements_notebook.txt
```

## 📖 Notebook Structure

### 1. 🏗️ Environment Setup
- Library imports and configuration
- Database connection establishment
- Error handling setup

### 2. 🔗 Database Connection
- Secure PostgreSQL connection
- Connection health verification
- Query execution framework

### 3. 📥 Data Loading
- Property data extraction
- Data shape and memory usage
- Initial data preview

### 4. 🔍 Data Quality Assessment
- Missing value analysis
- Data type validation
- Basic statistical summaries
- Key insights extraction

### 5. 📊 Data Visualization
- Price distribution histograms
- Property type breakdowns
- Price vs. size scatter plots
- Interactive Plotly charts

### 6. 📈 Statistical Analysis
- Correlation matrix heatmaps
- Price correlation rankings
- ANOVA testing by property type
- Pearson correlation significance

### 7. 💰 Market Analysis
- Price segmentation (Budget/Mid-Range/Premium/Luxury)
- City-based analysis
- Investment opportunity identification
- Price per square foot insights

## 🎯 Usage Examples

### Basic Analysis
```python
# Load and analyze data
df = db.get_data("SELECT * FROM properties LIMIT 1000")
print(f"Loaded {len(df)} properties")

# Quick statistics
print(df['current_price'].describe())
```

### Custom Queries
```python
# Analyze specific markets
query = """
SELECT city, AVG(current_price) as avg_price, COUNT(*) as count
FROM properties 
WHERE state = 'CA' 
GROUP BY city 
ORDER BY avg_price DESC
"""
city_analysis = db.get_data(query)
```

## 🚨 Troubleshooting

### Database Connection Issues
```python
# Test connection manually
try:
    engine = create_engine('your_connection_string')
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Missing Libraries
```bash
# Install specific library
pip install plotly

# Install all requirements
pip install -r requirements_notebook.txt
```

### Memory Issues
```python
# Reduce data size
df_sample = df.sample(n=10000)  # Use sample for large datasets

# Check memory usage
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
```

## 📊 Sample Outputs

### Data Quality Report
```
📋 Data Quality Assessment:
✅ No missing data!

📈 Numeric Data Summary:
       current_price    bedrooms    bathrooms
count      1000.000    1000.000     1000.000
mean     450000.000       3.200        2.100
std      200000.000       1.100        0.800
```

### Market Insights
```
💰 Price Segments:
Budget      (< $300k): 250 properties, avg $245k
Mid-Range   ($300-500k): 400 properties, avg $398k
Premium     ($500-750k): 250 properties, avg $623k
Luxury      (> $750k): 100 properties, avg $1.2M
```

## 🔄 Updates and Maintenance

### Updating Requirements
```bash
# Update all packages
pip install --upgrade -r requirements_notebook.txt

# Update specific package
pip install --upgrade plotly
```

### Database Schema Changes
If the database schema changes, update the SQL queries in the notebook:
```python
# Update column names in queries
query = """
SELECT new_column_name, other_columns
FROM updated_table_name
WHERE conditions
"""
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your analysis or improvements
4. Test with sample data
5. Submit a pull request

## 📄 License

This notebook is part of the Real Estate Pipeline project. See the main project README for license information.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the database connection logs
3. Ensure all requirements are installed
4. Check the main project documentation

---

**Happy Analyzing! 📊🏠**
