# Errors that describe what went wrong in *business* terms. crud.py raises
# them; main.py decides what HTTP response each one becomes. crud.py never
# has to know about status codes.


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ItemNotFound(AppError):
    status_code = 404
    code = "item_not_found"

    def __init__(self, item_id: int):
        super().__init__(f"Item {item_id} not found")


class DuplicateItemName(AppError):
    status_code = 409
    code = "duplicate_name"

    def __init__(self, name: str):
        super().__init__(f"An item named '{name}' already exists")


class ItemStillInStock(AppError):
    status_code = 409
    code = "item_in_stock"

    def __init__(self, item_id: int, quantity: int):
        super().__init__(f"Item {item_id} still has {quantity} in stock; set quantity to 0 first")


class EmptyUpdate(AppError):
    status_code = 400
    code = "empty_update"

    def __init__(self):
        super().__init__("Send at least one non-null field to update")
