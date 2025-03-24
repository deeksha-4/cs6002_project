#ifndef NETWORK_H
#define NETWORK_H

#include <bits/stdc++.h>
#include "agent.h"

using namespace std;

class Network
{
public:
    vector<Agent *> agents;
    int numAgents;
    string mechanism;

    Network(int numAgents, string mechanism);
};

#endif
