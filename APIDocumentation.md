E-Commerce Variants API Documentation

This document outlines all the REST API endpoints available in the system, strictly following the required specifications. The API is divided into Admin operations and Storefront operations.

Base URL: http://localhost:8000 (or as configured in your environment).

-- Admin Endpoints --

Products

1. Create Product

Method: POST

Endpoint: /products/

Request Body:

{
  "name": "New Product",
  "description": "Product Description",
  "base_price": "25.00"
}


Response (201 Created): Returns the created product object.

2. List All Products

Method: GET

Endpoint: /products/

Response (200 OK): Returns a list of all products (base details).

3. Get Product Details

Method: GET

Endpoint: /products/<id>/

Response (200 OK): Returns a product with all its variant types and options.

4. Update Product

Method: PUT (or PATCH)

Endpoint: /products/<id>/

Request Body: Fields to update (e.g., {"base_price": "29.99"}).

Response (200 OK): Returns the updated product.

5. Delete Product

Method: DELETE

Endpoint: /products/<id>/

Response: Returns 204 No Content on success. Fails (400 Bad Request) if the product is linked to historical orders.

Variant Types & Options

6. Add Variant Type

Method: POST

Endpoint: /products/<id>/variants/

Request Body: {"name": "Color", "options": ["Red", "Blue"]}

7. Add Variant Option

Method: POST

Endpoint: /products/<id>/variants/<vid>/options/

Request Body: {"option": "Green"}

8. Delete Variant Type

Method: DELETE

Endpoint: /products/<id>/variants/<vid>/

Description: Removes a variant type. Triggers a Smart Sync to archive affected combinations if previously ordered.

9. Delete Variant Option

Method: DELETE

Endpoint: /variants/options/<oid>/

Description: Removes a specific option. Triggers a Smart Sync.

Combinations Management

10. List Combinations for a Product

Method: GET

Endpoint: /products/<id>/combinations/

Response (200 OK): Returns a list of all combinations (SKUs) for the product, including their specific additional_price and stock.

11. Update Combination Price/Stock

Method: PUT

Endpoint: /combinations/<cid>/

Description: Set additional price and stock for a specific combination.

Request Body:

{
  "additional_price": "5.00",
  "stock": 100
}


Storefront Endpoints

12. Get Product for UI

Method: GET

Endpoint: /products/<id>/

Description: Returns product base details + variant types + options for building the dynamic UI selectors.

13. Combination Lookup

Method: POST

Endpoint: /products/<id>/combinations/lookup/

Description: Pass the selected option IDs to resolve the final combination, price, and stock dynamically.

Request Body: {"option_ids": [1, 3]} (Send [] for simple products).

Response (200 OK):

{
  "combination_id": 4,
  "additional_price": "2.00",
  "final_price": "21.99",
  "stock": 5,
  "in_stock": true
}


14. Place Order (Atomic Checkout)

Method: POST

Endpoint: /orders/

Description: Validates stock and deducts it atomically using pessimistic database locking.

Request Body:

{
  "combination_id": 4,
  "quantity": 2
}


Response (201 Created):

{
  "order_id": 101,
  "total": "43.98",
  "status": "confirmed"
}


Error Response (422 Unprocessable Entity): If stock is insufficient.
