#include "helper.h"
using namespace std;

int generate_random_number(int lower_bound, int upper_bound)
{
    return lower_bound + rand() % (upper_bound - lower_bound + 1);
}

bool is_connected(vector<vector<int>> &graph, int numAgents)
{
    vector<bool> vis(numAgents, 0);
    queue<int> q;
    q.push(0);
    vis[0] = true;
    int peers_visited = 1;
    
    while (!q.empty())
    {
        int curr = q.front();
        q.pop();
        
        for (auto neighbor : graph[curr])
        {
            if (!vis[neighbor])
            {
                vis[neighbor] = 1;
                q.push(neighbor);
                peers_visited++;
            }
        }
    }
    
    return (peers_visited == numAgents);
}


vector<vector<int>> generate_graph(int numAgents)
{
    vector<vector<int>> graph;
    do
    {
        vector<int> degrees;
        for (int i = 0; i < numAgents; ++i)
        {
            degrees.push_back(generate_random_number(1, 3));
        }
        graph = {};
        for (int i = 0; i < numAgents; i++)
        {
            graph.push_back(vector<int>());
        }
        for (int i = 0; i < numAgents; i++)
        {
            for (int j = i + 1; j < numAgents; j++)
            {
                if (degrees[i] > 0 && degrees[j] > 0)
                {
                    degrees[i]--;
                    degrees[j]--;
                    graph[i].push_back(j);
                    graph[j].push_back(i);
                }
            }
        }
    } while (!is_connected(graph, numAgents));

    return graph;
}
