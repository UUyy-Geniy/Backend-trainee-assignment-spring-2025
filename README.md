python -m pytest --cov=.


brew install grpcurl


# Проверка списка методов (должна работать reflection)
grpcurl -plaintext localhost:3000 list

# Пример вызова метода GetPVZList
grpcurl -plaintext -d '{}' localhost:3000 pvz.v1.PVZService/GetPVZList


http://localhost:9000/metrics