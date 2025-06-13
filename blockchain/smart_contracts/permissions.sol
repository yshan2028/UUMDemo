// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Permissions {
    // 定义角色
    enum Role { None, Merchant, Logistics, Customer }

    // 用户地址到角色的映射
    mapping(address => Role) private roles;

    // 事件
    event RoleAssigned(address indexed user, Role role);
    event AccessAttempt(address indexed user, string resource, bool success);

    // 修饰符：仅限特定角色访问
    modifier onlyRole(Role requiredRole) {
        require(roles[msg.sender] == requiredRole, "Access denied: insufficient permissions");
        _;
    }

    // 设置角色
    function assignRole(address user, Role role) public {
        roles[user] = role;
        emit RoleAssigned(user, role);
    }

    // 获取角色
    function getRole(address user) public view returns (Role) {
        return roles[user];
    }

    // 验证访问权限
    function checkAccess(string memory resource) public view returns (bool) {
        Role userRole = roles[msg.sender];
        bool hasAccess = false;

        if (
            (keccak256(abi.encodePacked(resource)) == keccak256(abi.encodePacked("items")) && userRole == Role.Merchant) ||
            (keccak256(abi.encodePacked(resource)) == keccak256(abi.encodePacked("shipping_address")) && userRole == Role.Logistics)
        ) {
            hasAccess = true;
        }

        emit AccessAttempt(msg.sender, resource, hasAccess);
        return hasAccess;
    }
}
