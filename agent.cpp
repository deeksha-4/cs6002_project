#include "agent.h"

Agent::Agent()
{
    agentID = agentIDctr++;
    allocation = 0;
    payment = 0;
    trueValuation = rand() % 100 + 1;
    reportedValuation = trueValuation;
    // compute sj
}