# create a volume
docker volume create pgdata

# launch a container
docker run -d --name=pg -p 5432:5432 -v pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=$PG_PASS postgres

# drop into postgres console
docker exec -it pg psql -U postgres

# or better yet, setup using a file

 sudo cat init.sql | docker exec -i pg psql -U postgres -d postgres
