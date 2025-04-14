from locust import HttpUser, between, task


class FullFlowUser(HttpUser):
    # Интервал между действиями в секундах
    wait_time = between(1, 2)

    def on_start(self):
        # Логинимся как модератор для операций, требующих роли moderator
        r_mod = self.client.post("/api/v1/dummyLogin", json={"role": "moderator"})
        if r_mod.status_code == 200:
            self.mod_token = r_mod.json().get("token")
        else:
            self.mod_token = None

        # Логинимся как сотрудник для операций, требующих роли employee
        r_emp = self.client.post("/api/v1/dummyLogin", json={"role": "employee"})
        if r_emp.status_code == 200:
            self.emp_token = r_emp.json().get("token")
        else:
            self.emp_token = None

    @task
    def full_flow(self):
        # Если не получили токены, прерываем выполнение
        if not self.mod_token or not self.emp_token:
            return

        headers_mod = {"Authorization": f"Bearer {self.mod_token}"}
        headers_emp = {"Authorization": f"Bearer {self.emp_token}"}

        # 1. Создаем ПВЗ с использованием модераторского токена
        with self.client.post(
            "/api/v1/pvz", json={"city": "Москва"}, headers=headers_mod, catch_response=True, name="Create PVZ"
        ) as response:
            if response.status_code in (200, 201):
                data = response.json()
                pvz_id = data.get("id")
                if not pvz_id:
                    response.failure("Создание ПВЗ: не получен id")
                    return
            else:
                response.failure(f"Создание ПВЗ провалилось. Статус: {response.status_code}")
                return

        # 2. Запускаем приёмку с использованием employee-токена
        with self.client.post(
            "/api/v1/receptions",
            json={"pvz_id": pvz_id},
            headers=headers_emp,
            catch_response=True,
            name="Start Reception",
        ) as response:
            if response.status_code not in (200, 201):
                # Если приёмка не запускается (например, уже активна или иной сбой),
                # помечаем ошибку и выходим.
                response.failure(f"Запуск приёмки провалился. Статус: {response.status_code}")
                return

        # 3. Добавляем товар (предполагается, что активная приёмка существует)
        with self.client.post(
            "/api/v1/products",
            json={"pvz_id": pvz_id, "type": "электроника"},
            headers=headers_emp,
            catch_response=True,
            name="Add Product",
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Добавление товара провалилось. Статус: {response.status_code}")
                return

        # 4. Опционально: закрываем приёмку с использованием модераторского токена
        with self.client.post(
            f"/api/v1/pvz/{pvz_id}/close_last_reception",
            headers=headers_emp,
            catch_response=True,
            name="Close Reception",
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Закрытие приёмки провалилось. Статус: {response.status_code}")
