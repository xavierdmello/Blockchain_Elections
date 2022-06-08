// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Election.sol";
import "./ElectionManager.sol";

// The ElectionDataAggregator returns bundles of data to minimize the amount of API calls used by the frontend.
// It should not be used by other contracts directly as it is a gas-inefficent way of getting data.
struct ElectionData {
    string electionName;
    address[] voters;
    Candidate[] candidates;
    address owner;
    uint candidateFee;
    uint electionEndTime;
    uint electionStartTime;
    bool closed;
}

struct Candidate {
    uint votes;
    string name;
    address candidateAddress;
}

struct BundledElection {
    Election election;
    string name;
}

contract ElectionDataAggregator {
    function getElectionsBundledWithNames(address _electionManager) public view returns(BundledElection[] memory) {
        ElectionManager electionManager = ElectionManager(_electionManager);
        Election[] memory elections = electionManager.getElections();
        BundledElection[] memory bundledElections = new BundledElection[](elections.length);

        for (uint256 i; i < elections.length; i++) {
            bundledElections[i] = BundledElection(elections[i], elections[i].electionName());
        }
        return bundledElections;
    }
    
    
    function getElectionData(address _election) public view returns(ElectionData memory) {
        Election election = Election(_election);
        
        //Create array of Candidates
        address[] memory candidateAddresses = election.getCandidates();
        Candidate[] memory candidates = new Candidate[](candidateAddresses.length);
        for (uint i; i < candidateAddresses.length; i++) {
            address candidateAddress = candidateAddresses[i];
            candidates[i] = Candidate(election.votes(candidateAddress), election.candidateNames(candidateAddress), candidateAddress);
        }

        return ElectionData(election.electionName(), election.getVoters(), candidates, election.owner(),election.candidateFee(), election.electionEndTime(), election.electionStartTime(), election.isClosed());
    }

    function getAllElectionsData(address _electionManager) public view returns(ElectionData[] memory) {
        ElectionManager electionManager = ElectionManager(_electionManager);
        Election[] memory elections = electionManager.getElections();
        ElectionData[] memory allElectionsData = new ElectionData[](elections.length);

        for (uint256 i; i < elections.length; i++) {
            allElectionsData[i] = getElectionData(address(elections[i]));
        }

        return allElectionsData;
    }
    
}
