// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DVSS-PPA Permissions Contract
 * @author yshan2028
 * @dev Smart contract for managing access permissions
 */
contract DVSSPermissions {

    // Events
    event RoleGranted(address indexed user, string role);
    event RoleRevoked(address indexed user, string role);
    event PermissionUpdated(address indexed user, string permission, bool granted);

    // Structures
    struct UserRole {
        string role;
        bool active;
        uint256 grantedAt;
    }

    struct Permission {
        bool canRead;
        bool canWrite;
        bool canDelete;
        bool canAdmin;
    }

    // State variables
    mapping(address => UserRole) public userRoles;
    mapping(address => Permission) public userPermissions;
    mapping(string => Permission) public rolePermissions;

    address public owner;
    uint256 public totalUsers;

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    modifier onlyAdmin() {
        require(userPermissions[msg.sender].canAdmin, "Admin permission required");
        _;
    }

    constructor() {
        owner = msg.sender;

        // Initialize default role permissions
        rolePermissions["merchant"] = Permission(true, true, false, false);
        rolePermissions["logistics"] = Permission(true, true, false, false);
        rolePermissions["payment"] = Permission(true, true, false, false);
        rolePermissions["admin"] = Permission(true, true, true, true);

        // Grant admin role to owner
        userRoles[owner] = UserRole("admin", true, block.timestamp);
        userPermissions[owner] = rolePermissions["admin"];
        totalUsers = 1;
    }

    /**
     * @dev Grant role to user
     * @param user User address
     * @param role Role name
     */
    function grantRole(address user, string memory role) external onlyAdmin {
        require(user != address(0), "Invalid user address");
        require(bytes(role).length > 0, "Role cannot be empty");

        userRoles[user] = UserRole(role, true, block.timestamp);
        userPermissions[user] = rolePermissions[role];

        if (userRoles[user].grantedAt == block.timestamp) {
            totalUsers++;
        }

        emit RoleGranted(user, role);
    }

    /**
     * @dev Check if user has permission for operation
     * @param user User address
     * @param operation Operation type (read/write/delete/admin)
     * @return bool Permission status
     */
    function hasPermission(address user, string memory operation)
        external view returns (bool) {

        if (!userRoles[user].active) {
            return false;
        }

        Permission memory perm = userPermissions[user];

        if (keccak256(bytes(operation)) == keccak256(bytes("read"))) {
            return perm.canRead;
        } else if (keccak256(bytes(operation)) == keccak256(bytes("write"))) {
            return perm.canWrite;
        } else if (keccak256(bytes(operation)) == keccak256(bytes("delete"))) {
            return perm.canDelete;
        } else if (keccak256(bytes(operation)) == keccak256(bytes("admin"))) {
            return perm.canAdmin;
        }

        return false;
    }

    /**
     * @dev Get user role information
     * @param user User address
     * @return UserRole User role details
     */
    function getUserRole(address user) external view returns (UserRole memory) {
        return userRoles[user];
    }
}