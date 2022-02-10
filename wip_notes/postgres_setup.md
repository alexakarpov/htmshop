# create a volume
docker volume create pgdata

# launch a container
docker run -d --name=pgdb -p 5432:5432 -v pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD postgres

# drop into postgres console
docker exec -it pgdb psql -U postgres

# or better yet, setup using a file

 sudo cat init.sql | docker exec -i pgdb psql -U postgres -d postgres

# other db notes

## sequence last value example
select last_value from orders_order_id_seq;

## setting sequence value
SELECT setval('orders_order_id_seq', 50042);
