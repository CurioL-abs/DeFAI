// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract YieldVaultERC4626 {
    string public name = "Demo Vault";
    string public symbol = "dVAULT";
    address public owner;
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalAssets;

    constructor() {
        owner = msg.sender;
    }

    function deposit() external payable returns (uint256) {
        uint256 sharesToMint = msg.value;
        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
        totalAssets += msg.value;
        return sharesToMint;
    }

    function withdraw(uint256 shareAmount) external {
        require(shares[msg.sender] >= shareAmount, "Not enough shares");
        uint256 assets = shareAmount;
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        totalAssets -= assets;
        payable(msg.sender).transfer(assets);
    }

    function simulateYield(uint256 amount) external {
        require(msg.sender == owner, "owner only");
        totalAssets += amount;
    }
}
