import json
import boto3

# DynamoDB resource
dynamodb = boto3.resource("dynamodb")

# Order table
order_table = dynamodb.Table("my-orders")

# Start order numbers at 1001.
order_number = 1001


def generate_order_id():
    global order_number
    order_id = f"ORD{order_number:04d}"
    order_number += 1
    return order_id


def lambda_handler(event, context):
    orders = [
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객003",
            "Items": [
                {"ProductName": "포도", "Quantity": 1, "Price": 2000},
            ],
            "ShippingAddress": "부산광역시 해운대구",
            "GiftMessage": "감사합니다!",
            "DeliveryInstructions": "경비실에 맡겨주세요",
        },
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객004",
            "Items": [
                {"ProductName": "딸기", "Quantity": 4, "Price": 3000},
                {"ProductName": "사과", "Quantity": 2, "Price": 1000},
            ],
            "ShippingAddress": "대구광역시 중구 중앙로",
            "DiscountCode": "WELCOME2024",
            "DeliveryInstructions": "문 앞에 두세요",
        },
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객005",
            "Items": [
                {"ProductName": "체리", "Quantity": 5, "Price": 4500},
            ],
            "ShippingAddress": "인천광역시 연수구 송도동",
            "GiftMessage": "축하드립니다!",
        },
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객006",
            "Items": [
                {"ProductName": "배", "Quantity": 3, "Price": 5000},
            ],
            "DiscountCode": "WELCOME2024",
        },
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객007",
            "Items": [
                {"ProductName": "망고", "Quantity": 10, "Price": 12000},
            ],
        },
        {
            "OrderID": generate_order_id(),
            "CustomerID": "고객008",
            "Items": [
                {"ProductName": "수박", "Quantity": 1, "Price": 15000},
            ],
            "ShippingAddress": "서울특별시 송파구 올림픽로",
            "GiftMessage": "생일 축하합니다!",
            "DeliveryInstructions": "부재 시 연락 부탁드립니다.",
            "AdditionalServices": "GiftWrap",
            "PriorityDelivery": True,
        },
    ]

    for order in orders:
        order_table.put_item(Item=order)

    return {
        "statusCode": 200,
        "body": json.dumps("Additional order data added successfully!"),
    }
