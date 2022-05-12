// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Election.sol";

contract ElectionManager {
    Election[] public elections;

    function createElection(
        string memory _electionName,
        uint256 _electionEndTime
    ) public returns (address) {
        Election newElection = new Election(
            msg.sender,
            _electionName,
            _electionEndTime
        );
        elections.push(newElection);
        return address(newElection);
    }

    function getElectionNames() public view returns (string[] memory) {
        string[] memory electionNames = new string[](elections.length);
        for (uint256 i; i < elections.length; i++) {
            electionNames[i] = elections[i].electionName();
        }
        return electionNames;
    }
}
