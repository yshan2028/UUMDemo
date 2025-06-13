// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Orders {
    // 订单结构体
    struct Order {
        string orderId;
        string status; // 状态：Processing, Shipped, Delivered, Cancelled
        uint256 timestamp;
    }

    // 订单 ID 到订单详情的映射
    mapping(string => Order) private orders;

    // 事件
    event OrderCreated(string indexed orderId, string status);
    event OrderUpdated(string indexed orderId, string status);

    // 创建订单
    function createOrder(string memory orderId, string memory status) public {
        require(bytes(orders[orderId].orderId).length == 0, "Order already exists");

        orders[orderId] = Order(orderId, status, block.timestamp);
        emit OrderCreated(orderId, status);
    }

    // 更新订单状态
    function updateOrderStatus(string memory orderId, string memory newStatus) public {
        require(bytes(orders[orderId].orderId).length != 0, "Order does not exist");

        orders[orderId].status = newStatus;
        emit OrderUpdated(orderId, newStatus);
    }

    // 查询订单
    function getOrder(string memory orderId) public view returns (string memory, string memory, uint256) {
        require(bytes(orders[orderId].orderId).length != 0, "Order does not exist");

        Order memory order = orders[orderId];
        return (order.orderId, order.status, order.timestamp);
    }
}
