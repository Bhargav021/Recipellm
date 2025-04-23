def clean_sql_query(sql):
    return sql.replace("```sql", "").replace("```", "").strip()

def format_sql_results(results, columns):
    if not results:
        return "<b>No results found.</b>"
    output = "<b>Query Results:</b><br>"
    for row in results:
        output += "<ul>"
        for col, val in zip(columns, row):
            output += f"<li><b>{col}:</b> {val}</li>"
        output += "</ul><br>"
    return output
