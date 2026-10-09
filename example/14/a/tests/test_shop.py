from sqlalchemy import text

from database import SessionLocal

ORDER_INFO = {"phone": "0300-1234567", "address": "12 Mall Road, Lahore"}


def new_product(client, admin, stock=5, price="10.50"):
    res = client.post("/products", headers=admin,
                      json={"name": "Mug", "price": price, "stock": stock})
    assert res.status_code == 201
    return res.json()


# ----------------------------------------------------------- auth ----

def test_register_is_always_customer(client):
    res = client.post("/register", json={"username": "sneaky", "password": "password123",
                                         "role": "admin"})
    assert res.status_code == 201
    assert res.json()["role"] == "customer"


def test_no_token_is_401(client):
    assert client.get("/products").status_code == 401
    assert client.get("/me").status_code == 401


# ---------------------------------------------------------- roles ----

def test_customer_gets_403_on_admin_routes(client, make_customer):
    cust = make_customer("cora")
    assert client.post("/products", headers=cust, json={"name": "x", "price": "1"}).status_code == 403
    assert client.get("/orders", headers=cust).status_code == 403
    assert client.get("/users", headers=cust).status_code == 403


def test_admin_cannot_change_own_role(client, admin):
    me = client.get("/me", headers=admin).json()
    assert client.patch(f"/users/{me['id']}/role", headers=admin,
                        json={"role": "customer"}).status_code == 400


def test_promote_takes_effect_immediately(client, admin, make_customer):
    dan = make_customer("dan")
    assert client.get("/users", headers=dan).status_code == 403
    dan_id = client.get("/me", headers=dan).json()["id"]
    assert client.patch(f"/users/{dan_id}/role", headers=admin, json={"role": "admin"}).status_code == 200
    # Same old token, which still says "customer": the DB role wins.
    assert client.get("/users", headers=dan).status_code == 200


# -------------------------------------------------------- hashed ids ----

def test_ids_are_hashed(client, admin):
    product = new_product(client, admin)
    assert isinstance(product["id"], str) and not product["id"].isdigit()
    assert client.get(f"/products/{product['id']}", headers=admin).status_code == 200
    assert client.get("/products/1", headers=admin).status_code == 404
    assert client.get("/products/notreal", headers=admin).status_code == 404


# ---------------------------------------------------- products/stock ----

def test_stock_cannot_go_negative(client, admin):
    product = new_product(client, admin, stock=2)
    url = f"/products/{product['id']}/stock"
    assert client.patch(url, headers=admin, json={"change": -3}).status_code == 400
    assert client.patch(url, headers=admin, json={"change": 8}).json()["stock"] == 10


def test_deleted_product_is_hidden_from_customers(client, admin, make_customer):
    cust = make_customer("hana")
    product = new_product(client, admin)
    assert client.delete(f"/products/{product['id']}", headers=admin).status_code == 204
    assert client.get(f"/products/{product['id']}", headers=cust).status_code == 404
    assert product["id"] not in [p["id"] for p in client.get("/products", headers=cust).json()]
    # Admin still sees it, so it can be brought back.
    assert client.get(f"/products/{product['id']}", headers=admin).json()["is_active"] is False


# ------------------------------------------------------------ orders ----

def test_order_reduces_stock_and_cancel_restores(client, admin, make_customer):
    cust = make_customer("eve")
    product = new_product(client, admin, stock=5, price="10.50")
    res = client.post("/orders", headers=cust,
                      json={"items": [{"product_id": product["id"], "quantity": 2}], **ORDER_INFO})
    assert res.status_code == 201
    order = res.json()
    assert order["total"] == "21.00"
    assert client.get(f"/products/{product['id']}", headers=cust).json()["stock"] == 3

    assert client.post(f"/orders/{order['id']}/cancel", headers=cust).json()["status"] == "cancelled"
    assert client.get(f"/products/{product['id']}", headers=cust).json()["stock"] == 5


def test_cannot_oversell(client, admin, make_customer):
    cust = make_customer("finn")
    product = new_product(client, admin, stock=1)
    res = client.post("/orders", headers=cust,
                      json={"items": [{"product_id": product["id"], "quantity": 2}], **ORDER_INFO})
    assert res.status_code == 409
    # Nothing changed: the failed order took no stock.
    assert client.get(f"/products/{product['id']}", headers=cust).json()["stock"] == 1


def test_customer_cannot_see_others_orders(client, admin, make_customer):
    gus, ivy = make_customer("gus"), make_customer("ivy")
    product = new_product(client, admin)
    order = client.post("/orders", headers=gus,
                        json={"items": [{"product_id": product["id"], "quantity": 1}], **ORDER_INFO}).json()
    assert client.get(f"/orders/{order['id']}", headers=ivy).status_code == 404
    assert client.post(f"/orders/{order['id']}/cancel", headers=ivy).status_code == 404
    assert order["id"] not in [o["id"] for o in client.get("/orders/mine", headers=ivy).json()]
    assert client.get(f"/orders/{order['id']}", headers=admin).status_code == 200


def test_status_flow(client, admin, make_customer):
    cust = make_customer("joe")
    product = new_product(client, admin)
    order = client.post("/orders", headers=cust,
                        json={"items": [{"product_id": product["id"], "quantity": 1}], **ORDER_INFO}).json()
    url = f"/orders/{order['id']}/status"
    assert client.patch(url, headers=admin, json={"status": "delivered"}).status_code == 400
    assert client.patch(url, headers=admin, json={"status": "shipped"}).status_code == 200
    # Shipped orders can't be cancelled by the customer any more.
    assert client.post(f"/orders/{order['id']}/cancel", headers=cust).status_code == 400


def test_address_is_encrypted_in_database(client, admin, make_customer):
    cust = make_customer("kim")
    product = new_product(client, admin)
    order = client.post("/orders", headers=cust,
                        json={"items": [{"product_id": product["id"], "quantity": 1}], **ORDER_INFO}).json()
    # The API decrypts it for the owner...
    assert order["address"] == ORDER_INFO["address"]
    # ...but the database only ever holds ciphertext.
    with SessionLocal() as db:
        stored = db.execute(text("SELECT address_encrypted, phone_encrypted FROM minishop_orders")).all()
    for address, phone in stored:
        assert ORDER_INFO["address"] not in address
        assert ORDER_INFO["phone"] not in phone


# ------------------------------------------------------------- seed ----

def test_seed_users_can_log_in(client):
    for username, role in (("admin", "admin"), ("alice", "customer")):
        res = client.post("/login", json={"username": username, "password": f"{username}-password"})
        assert res.status_code == 200
        me = client.get("/me", headers={"Authorization": f"Bearer {res.json()['access_token']}"})
        assert me.json()["role"] == role
