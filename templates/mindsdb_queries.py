from string import Template

MODEL_CREATION_QUERY = Template(
  '''
    CREATE MODEL npm_predictions.${package}_prediction_model
      FROM files (
      SELECT * FROM ${package}
      )
    PREDICT date, downloads
    ORDER BY date
    HORIZON ${prediction_date};                       
''')

RETRIEVE_PREDICTION_QUERY = Template(
  '''
  SELECT m.date AS date, m.downloads AS downloads
    FROM mindsdb.${package}_prediction_model AS m
    JOIN files.${package} AS t
    WHERE t.date > LATEST;
''')