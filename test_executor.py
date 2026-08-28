from app.executor import execute_query

sql = "SELECT album.title FROM album JOIN artist ON album.artist_id = artist.artist_id WHERE artist.name = 'AC/DC'"
result = execute_query(sql)
print("Columns:", result["columns"])
for row in result["rows"]:
    print(row)