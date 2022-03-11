// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "/Users/shredder/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC721/ERC721.sol";

contract E721 is ERC721("Test", "T") {

    uint256 private tokenID = 1;

    function mint() external {
        _safeMint(msg.sender, tokenID);
        ++tokenID;
    }

}
