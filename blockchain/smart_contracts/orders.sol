// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DVSS-PPA Orders Contract
 * @author yshan2028
 * @dev Smart contract for managing order processing
 */
contract DVSSOrders {

    // Events
    event OrderCreated(string indexed orderId, address indexed customer, uint256 amount);
    event OrderUpdated(string indexed orderId, OrderStatus status);
    event ShareStored(string indexed orderId, string shareId);

    // Enums
    enum OrderStatus {
        Created,
        Processing,
        Shipped,
        Delivered,
        Completed,
        Cancelled
    }

    // Structures
    struct Order {
        string orderId;
        address customer;
        uint256 amount;
        OrderStatus status;
        uint256 createdAt;
        string[] shareIds;
    }

    struct ShareMetadata {
        string shareId;
        string orderId;
        uint256 threshold;
        uint256 createdAt;
        bool isActive;
    }

    // State variables
    mapping(string => Order) public orders;
    mapping(string => ShareMetadata) public shares;
    mapping(address => string[]) public customerOrders;

    address public owner;
    uint256 public totalOrders;
    uint256 public totalShares;

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    modifier orderExists(string memory orderId) {
        require(bytes(orders[orderId].orderId).length > 0, "Order does not exist");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Create new order
     * @param orderId Unique order identifier
     * @param customer Customer address
     * @param amount Order amount
     */
    function createOrder(
        string memory orderId,
        address customer,
        uint256 amount
    ) external {
        require(bytes(orderId).length > 0, "Order ID cannot be empty");
        require(customer != address(0), "Invalid customer address");
        require(amount > 0, "Amount must be greater than 0");
        require(bytes(orders[orderId].orderId).length == 0, "Order already exists");

        orders[orderId].orderId = orderId;
        orders[orderId].customer = customer;
        orders[orderId].amount = amount;
        orders[orderId].status = OrderStatus.Created;
        orders[orderId].createdAt = block.timestamp;

        customerOrders[customer].push(orderId);
        totalOrders++;

        emit OrderCreated(orderId, customer, amount);
    }

    /**
     * @dev Store secret share for order
     * @param orderId Order identifier
     * @param shareId Share identifier
     * @param threshold Reconstruction threshold
     */
    function storeShare(
        string memory orderId,
        string memory shareId,
        uint256 threshold
    ) external orderExists(orderId) {
        require(bytes(shareId).length > 0, "Share ID cannot be empty");
        require(threshold > 0, "Threshold must be greater than 0");
        require(!shares[shareId].isActive, "Share already exists");

        shares[shareId] = ShareMetadata({
            shareId: shareId,
            orderId: orderId,
            threshold: threshold,
            createdAt: block.timestamp,
            isActive: true
        });

        orders[orderId].shareIds.push(shareId);
        totalShares++;

        emit ShareStored(orderId, shareId);
    }

    /**
     * @dev Get order details
     * @param orderId Order identifier
     * @return Order details
     */
    function getOrder(string memory orderId)
        external view orderExists(orderId) returns (
            string memory,
            address,
            uint256,
            OrderStatus,
            uint256
        ) {
        Order storage order = orders[orderId];
        return (
            order.orderId,
            order.customer,
            order.amount,
            order.status,
            order.createdAt
        );
    }

    /**
     * @dev Get contract statistics
     * @return totalOrders Total number of orders
     * @return totalShares Total number of shares
     */
    function getStats() external view returns (uint256, uint256) {
        return (totalOrders, totalShares);
    }
}