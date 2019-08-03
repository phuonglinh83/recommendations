
## Install dependencies

Install required packages: : `scipy, pandas, psycopg2, numpy`

```pip install -r requirements.txt```

## Set database url:

Set the env variable `DATABSE_URL` for the database connection string. For example, for postgres on local:

```export DATABASE_URL=postgres://`whoami`@localhost:5432/<db_name>```

## Run

To bootstrap the dabase with initial activites and ratings:

``` python db_boostrap.py```

To recompute recommendations with new activites:

``` python run.py```
