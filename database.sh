podman run -d \
  --replace \
  --name postgres_grand_selve \
  -e POSTGRES_USER=grand_selve \
  -e POSTGRES_PASSWORD=jesus \
  -e POSTGRES_DB=grand_selve \
  -p 5432:5432 \
  -v "$PWD/postgres_data":/var/lib/postgresql/data:Z \
  docker.io/library/postgres:16
