#include "helper.h"
#include "network.h"

using namespace std;

Network::Network(int numAgents, string mechanism)
{
    this->numAgents = numAgents;
    this->mechanism = mechanism;
    vector<vector<int>> graph = generate_graph(numAgents);
    for (int i = 0; i < numAgents; i++)
    {
        Agent *agent = new Agent();
        agent->neighbors = graph[i];
        agents.push_back(agent);
    }
}