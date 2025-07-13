Local data is organized into three groupings following the [medallion
architecture](https://www.databricks.com/glossary/medallion-architecture):

* **Bronze** (raw data):

The Bronze layer is where we land all the data from external source systems. The data structures in
this layer correspond to the source system data structures "as-is," along with any additional
metadata fields that capture the load date/time, process ID, etc.

* **Silver** (cleansed and transformed):

In the Silver layer, the data from the Bronze layer is matched, merged, conformed and cleansed.  The
Silver layer brings the data from different Bronze layer sources together.


* **Gold** (curated "business-level" datasets):

Data in the Gold layer is typically organized in consumption/presentation-ready, "project-specific"
datasets.  The Gold layer datasets can be used for modeling and reporting.  The final layer of data
transformations and data quality rules are applied here.
