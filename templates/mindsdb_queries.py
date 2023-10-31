from string import Template

SQL_PACKAGE_QUERY = Template('''
SELECT date, downloads FROM pypi_datasource.overall 
    WHERE package="$package"
    AND mirrors=true 
    LIMIT 500'
''')