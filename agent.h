#ifndef AGENT_H
#define AGENT_H

#include <bits/stdc++.h>

using namespace std;

int agentIDctr = 0;

class Agent
{
public:
    int agentID;
    int trueValuation;
    int reportedValuation;
    int allocation;
    int payment;
    vector<int> neighbors;
    vector<int> sj;

    Agent();
};

#endif