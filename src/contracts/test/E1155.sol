// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "/home/shredder/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC1155/ERC1155.sol";

contract E1155 is ERC1155("lol") {

    uint256 private tokenID = 1;

    function mint() external {
        _mint(msg.sender, tokenID, 1, '');
        ++tokenID;
    }

}
