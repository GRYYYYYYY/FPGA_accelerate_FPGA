    bool isPartOfExistingRoute(int parent, int child) const {
        int endR = getNode(child);
        if (endR == -1) return false;
        int p = TLD(endR).prev;
        if (p != -1) {
            if (TLD(endR).visited == TLD(parent).visited) return false;
            if (p == parent && ns[child].preserved) return true;
        }
        return false;
    }

    bool isExcluded(int parent, int child) {
        if (isPartOfExistingRoute(parent, child)) return false;
        // super.isExcluded (UltraScale+; children are already allowed-tile from the export)
        if (ns[child].preserved) return true;
        int childRnode = getNode(child);
        if (ns[child].isPinfeed) {
            if (childRnode != -1) {
                // keep
            } else {
                // !lutRoutethru
                if (!hasLaguna) return true;
                if (!ns[child].pinfeedLeadsToLaguna) return true;
            }
        }
        if (!hasLaguna && ns[child].isLaguna) return true;
        if (childRnode != -1 && ns[childRnode].arcLockedInit && TLD(childRnode).prev != parent) return true;
        return false;
    }

