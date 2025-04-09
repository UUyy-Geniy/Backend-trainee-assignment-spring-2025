
!!Таблица с токенами
Таблица с токенами (`auth_tokens`) нужна для реализации **управления сессиями пользователей** и **безопасной аутентификации**. Вот ключевые причины:

---

### 1. **Хранение активных токенов**
- Каждый токен — это **уникальный ключ доступа** для пользователя.
- Таблица позволяет:
  - Отслеживать все выданные токены
  - Автоматически **аннулировать просроченные токены** (через `expires_at`)
  - Реализовать **принудительный выход из системы** (например, удаление токена при подозрении на взлом)

---

### 2. **Соответствие требованиям из ТЗ**
Согласно вашему swagger.yaml:
- Есть методы `/dummyLogin`, `/login`, возвращающие токены
- Токены должны проверяться при каждом запросе (securitySchemes: bearerAuth)

Таблица даёт возможность **валидировать токены** при каждом запросе:
```python
async def get_current_user(token: str, conn) -> User:
    result = await conn.execute(
        select(auth_tokens).where(
            auth_tokens.c.token == token,
            auth_tokens.c.expires_at > func.now()
        )
    )
    token_data = result.fetchone()
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return await get_user_by_id(token_data.user_id, conn)
```

---

### 3. **Безопасность**
- **Отсутствие JWT-уязвимостей**: В отличие от JWT, где токен нельзя отозвать до истечения срока, здесь можно мгновенно удалить токен из БД.
- **Контроль сессий**: Для важных систем (как в вашем ТЗ) часто требуется:
  - Вести историю входов
  - Ограничивать количество активных сессий
  - Реализовывать "выход со всех устройств"

---

### 4. **Реализация /dummyLogin и /login**
- При вызове `/dummyLogin` или `/login`:
  1. Генерируется уникальный токен
  2. Записывается в таблицу `auth_tokens`
  3. Возвращается пользователю

Пример для `/dummyLogin`:
```python
async def dummy_login(role: UserRole, conn):
    # Создаём временного пользователя (для демо)
    user_id = await create_temp_user(role, conn)
    
    # Генерируем токен
    token = generate_secure_token()
    expires_at = datetime.now() + timedelta(hours=12)
    
    # Сохраняем в БД
    await conn.execute(
        auth_tokens.insert().values(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
    )
    return {"token": token}
```

---

### 5. **Оптимизация производительности**
- Индекс по полю `token` обеспечивает быстрый поиск
- Периодическая очистка старых токенов:
```sql
DELETE FROM auth_tokens WHERE expires_at < NOW();
```

---

### Альтернатива: JWT
Если бы использовались JWT-токены:
- ✅ Не нужно хранить в БД
- ❌ Невозможно отозвать токен до истечения срока
- ❌ Сложнее реализовать контроль сессий

Для вашего ТЗ (где нужен строгий контроль доступа) таблица с токенами — более безопасное решение.

---

### Структура таблицы
| Поле        | Тип       | Описание                     |
|-------------|-----------|------------------------------|
| `token`     | `STRING`  | Уникальный ключ (Primary Key)|
| `user_id`   | `UUID`    | Связь с пользователем        |
| `expires_at`| `TIMESTAMP`| Срок действия токена        |

```python
# Пример использования
async def some_protected_route(token: str = Depends(oauth2_scheme)):
    async with conn() as conn:
        user = await get_current_user(token, conn)
        # ... логика ...
``` 

Таблица `auth_tokens` — обязательный компонент для реализации требований вашего ТЗ по безопасности и управлению доступом.