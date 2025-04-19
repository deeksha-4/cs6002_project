#include "gurobi_c++.h"
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <cmath>
#include <sstream>

using namespace std;

// Helper to generate all subsets (powerset) of a set
vector<set<int>> generatePowerset(const vector<int>& inputSet) {
  int n = inputSet.size();
  vector<set<int>> powerset;
  for (int mask = 0; mask < (1 << n); ++mask) {
    set<int> subset;
    for (int j = 0; j < n; ++j) {
      if (mask & (1 << j)) subset.insert(inputSet[j]);
    }
    powerset.push_back(subset);
  }
  return powerset;
}

// Helper to generate a string name for the variable
string makeVarName(int i, int v, const set<int>& r) {
  stringstream ss;
  ss << "theta_" << i << "_" << v << "_{";
  bool first = true;
  for (int elem : r) {
    if (!first) ss << ",";
    ss << elem;
    first = false;
  }
  ss << "}";
  return ss.str();
}

int main() {
  try {
    GRBEnv env = GRBEnv();
    GRBModel model = GRBModel(env);

    // Example data for multiple thetai:
    vector<int> b = {2, 1}; // For i=0: v₀ ∈ [0,2]; for i=1: v₁ ∈ [0,1]
    vector<vector<int>> R = {{1,2}, {3}}; // R₀ = {1,2}; R₁ = {3}

    // Store each Gurobi variable as a map indexed by (i, v, r)
    // We use vector<int> for r to make it usable as a key
    map<tuple<int, int, vector<int>>, GRBVar> thetaVars;

    for (int i = 0; i < b.size(); ++i) {
      int bi = b[i];
      vector<int> Ri = R[i];

      // Generate powerset of Ri
      vector<set<int>> riSubsets = generatePowerset(Ri);

      for (int v = 0; v <= bi; ++v) {
        for (const auto& subset : riSubsets) {
          // Convert subset to vector to use as map key
          vector<int> rVec(subset.begin(), subset.end());
          string varName = makeVarName(i, v, subset);
          GRBVar var = model.addVar(0.0, 1.0, 0.0, GRB_BINARY, varName); // Binary variable for each (v, r)
          thetaVars[{i, v, rVec}] = var;
        }
      }
    }

    model.update(); // finalize variable creation

    // Example: print variable names
    for (const auto& [key, var] : thetaVars) {
      cout << var.get(GRB_StringAttr_VarName) << endl;
    }

  } catch (GRBException& e) {
    cout << "Error code = " << e.getErrorCode() << endl;
    cout << e.getMessage() << endl;
  } catch (...) {
    cout << "Exception during optimization" << endl;
  }

  return 0;
}
